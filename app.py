import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
from pathlib import Path
import sys
import json
import threading
import importlib.util
import re
import scripts.common_functions as fc
import traceback

# =========================================================
# CONFIGURAÇÕES
# =========================================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COR_FRAME = ("white", "#1f1f1f")
COR_TEXTO = ("black", "white")

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def caminho_arquivo(relative_path):
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path

CONFIG_FILE = caminho_arquivo("config.json")

def salvar_json(chave, valor):
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
    else:
        dados = {}

    dados[chave] = valor

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def salvar_config(dados_novos):
    dados = {}

    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)

    dados.update(dados_novos)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def carregar_json():
    if Path(CONFIG_FILE).exists():

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}

# =========================================================
# SPLASH SCREEN
# =========================================================

class SplashScreen(ctk.CTkToplevel):

    def __init__(self, parent):

        super().__init__(parent)
        self.parent = parent

        largura = 500
        altura = 375

        x = int((self.winfo_screenwidth() / 2) - (largura / 2))
        y = int((self.winfo_screenheight() / 2) - (altura / 2))

        self.geometry(f"{largura}x{altura}+{x}+{y}")
        self.overrideredirect(True)
        self.configure(fg_color="#111111")


        # =====================================================
        # LOGO
        # =====================================================

        caminho_logo = caminho_arquivo(Path("figs") / "logo_interface.jpeg")

        imagem = ctk.CTkImage(
            light_image=Image.open(caminho_arquivo(caminho_logo)),
            dark_image=Image.open(caminho_arquivo(caminho_logo)),
            size=(500, 375)
        )

        label_logo = ctk.CTkLabel(self,image=imagem,text="")
        label_logo.pack()

        self.after(100, self.carregar)


    def carregar(self):

        # =====================================================
        # IMPORTS PESADOS
        # =====================================================

        #global pd
        #import pandas as pd
        # Exemplos:
        # import lmstudio as lms
        # from langchain_community.vectorstores import FAISS
        self.after(1000, self.finalizar)


    def finalizar(self):

        self.destroy()
        self.parent.deiconify()
    

# =========================================================
# APLICAÇÃO PRINCIPAL
# =========================================================

class MainApp(ctk.CTk):
    

    def __init__(self):

        super().__init__()

        self.tema_atual = "light"
        self.geometry("1000x600")
        self.title("CPD-DNIT")
        self.resizable(True, True)

        caminho_icone = caminho_arquivo(Path("figs") / "logo_icone.ico")
        self.iconbitmap(caminho_arquivo(caminho_icone))

        # =====================================================
        # INTERFACE
        # =====================================================

        self.criar_interface()
        self.carregar_dados_salvos()

    def carregar_dados_salvos(self):
        dados = carregar_json()

        self.nm_processo.insert(0, dados.get("processo", ""))
        self.nm_edital.insert(0, dados.get("edital", ""))
        self.nm_contrato.insert(0, dados.get("contrato", ""))
        self.nm_modalidade_de_contratacao.insert(0, dados.get("modalidade-de-contratacao", ""))
        self.nm_rodovia.insert(0, dados.get("rodovia", ""))
        self.nm_extensao.insert(0, dados.get("extensao", ""))
        self.nm_lote.insert(0, dados.get("lote", ""))
        self.nm_versao_analise.insert(0, dados.get("numero-analise", ""))
        self.nm_numero_ult_rel.insert(0, dados.get("numero-ult-relatorio", ""))
        self.nm_analista.insert(0, dados.get("analista", ""))

        tipo_projeto = dados.get("tipo-de-projeto")
        if tipo_projeto:
            self.nm_tipo_projeto.set(tipo_projeto)

        fase = dados.get("fase-de-projeto")
        if fase:
            self.nm_fase.set(fase)
            self.carregar_scripts()
        
        arquivos = dados.get("arquivos-para-analisar")
        if arquivos:
            self.lbl_arquivos_analise.configure(
                text="\n".join(Path(a).name for a in arquivos)
            )

        diretorio = dados.get("diretorio-resultados")
        if diretorio:
            self.lbl_dir_resultados.configure(text=diretorio)

        rap = dados.get("arquivo-rap")
        if rap:
            self.label_rap.configure(text=rap)

    # =========================================================
    # INTERFACE
    # =========================================================

    def criar_interface(self):

        # =====================================================
        # FRAME SUPERIOR
        # =====================================================

        self.frame_superior = ctk.CTkFrame(self, fg_color=COR_FRAME)

        self.frame_superior.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        self.campos_superior()

        # =====================================================
        # FRAME ESQUERDO
        # =====================================================

        self.frame_esquerdo = ctk.CTkFrame(self, fg_color=COR_FRAME)

        self.frame_esquerdo.place(relx=0, rely=0.1, relwidth=0.5, relheight=0.85)

        self.campos_lado_esquerdo()

        # =====================================================
        # FRAME DIREITO
        # =====================================================

        self.frame_direito = ctk.CTkFrame(self, fg_color=COR_FRAME)

        self.frame_direito.place(relx=0.5, rely=0.1, relwidth=0.5, relheight=0.85)

        self.campos_lado_direito()

        # =====================================================
        # FRAME INFERIOR
        # =====================================================

        self.frame_inferior = ctk.CTkFrame(self, fg_color=COR_FRAME)

        self.frame_inferior.place(relx=0, rely=0.95, relwidth=1, relheight=0.05)

        self.campos_inferior()

    # =========================================================
    # ALTERNAR MODO ESCURO E MODO CLARO
    # =========================================================

    def alternar_tema(self):
        if self.tema_atual == "light":
            ctk.set_appearance_mode("dark")
            self.tema_atual = "dark"
            self.btn_tema.configure(text="☀️ Modo Claro")

        else:
            ctk.set_appearance_mode("light")
            self.tema_atual = "light"
            self.btn_tema.configure(text="🌙 Modo Escuro")

    # =========================================================
    # LOGO
    # =========================================================

    def atualizar_logo(self, event=None):
        return


    # =========================================================
    # LADO SUPERIOR
    # =========================================================

    def campos_superior(self):
        
        # =====================================================
        # TÍTULO
        # =====================================================
        
        titulo = ctk.CTkLabel(self.frame_superior, text="CPD-DNIT", font=("Arial", 28, "bold"), text_color="#223467")
        titulo.pack(pady=(20, 15))

    # =========================================================
    # LADO ESQUERDO
    # =========================================================

    def campos_lado_esquerdo(self):

        # =====================================================
        # FRAME FORMULÁRIO
        # =====================================================
        frame_formulario = ctk.CTkFrame(self.frame_esquerdo, fg_color="transparent")
        frame_formulario.pack(fill="x", padx=30, pady = (25,0))
        frame_formulario.grid_columnconfigure(1, weight=1)


        # =====================================================
        # PROCESSO
        # =====================================================

        self.lbl_processo = ctk.CTkLabel(frame_formulario, text="Processo", width=75, anchor="w")
        self.lbl_processo.grid(row=0, column=0, sticky="w", pady=2)

        self.nm_processo = ctk.CTkEntry(frame_formulario)
        self.nm_processo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # EDITAL
        # =====================================================

        self.lbl_edital = ctk.CTkLabel(frame_formulario, text="Edital", width=75, anchor="w")
        self.lbl_edital.grid(row=1, column=0, sticky="w")

        self.nm_edital = ctk.CTkEntry(frame_formulario)
        self.nm_edital.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # CONTRATO
        # =====================================================

        self.lbl_contrato = ctk.CTkLabel(frame_formulario, text="Contrato", width=75, anchor="w")
        self.lbl_contrato.grid(row=2, column=0, sticky="w")

        self.nm_contrato = ctk.CTkEntry(frame_formulario)
        self.nm_contrato.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # MODALIDADE
        # =====================================================

        self.lbl_modalidade = ctk.CTkLabel(frame_formulario, text="Modalidade de contratação", width=75, anchor="w")
        self.lbl_modalidade.grid(row=3, column=0, sticky="w")

        self.nm_modalidade_de_contratacao = ctk.CTkEntry(frame_formulario)
        self.nm_modalidade_de_contratacao.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # BR
        # =====================================================

        self.lbl_rodovia = ctk.CTkLabel(frame_formulario, text="Rodovia", width=75, anchor="w")
        self.lbl_rodovia.grid(row=4, column=0, sticky="w")

        self.nm_rodovia = ctk.CTkEntry(frame_formulario, placeholder_text="BR no formato XXX/UF. Ex: 123/DF")
        self.nm_rodovia.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # EXTENSÃO
        # =====================================================

        self.lbl_extensao = ctk.CTkLabel(frame_formulario, text="Extensão", width=75, anchor="w")
        self.lbl_extensao.grid(row=5, column=0, sticky="w")

        self.nm_extensao = ctk.CTkEntry(frame_formulario, placeholder_text="")
        self.nm_extensao.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # LOTE
        # =====================================================

        self.lbl_lote = ctk.CTkLabel(frame_formulario, text="Lote", width=75, anchor="w")
        self.lbl_lote.grid(row=6, column=0, sticky="w")

        self.nm_lote = ctk.CTkEntry(frame_formulario, placeholder_text="")
        self.nm_lote.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # TIPO DE PROJETO
        # =====================================================

        self.lbl_tipo_projeto = ctk.CTkLabel(frame_formulario, text="Tipo de projeto", width=75, anchor="w")
        self.lbl_tipo_projeto.grid(row=7, column=0, sticky="w")

        tipo_projeto = [
            "Manutenção",
            "Implantação",
            "Misto",
            "Duplicação",
            "OAE",
            "Proarte"
        ]
        self.nm_tipo_projeto = ctk.CTkOptionMenu(frame_formulario, values=tipo_projeto)
        self.nm_tipo_projeto.grid(row=7, column=1, sticky="ew", padx=(10, 0), pady=2)
        self.nm_tipo_projeto.set("Tipo...")

        # =====================================================
        # FASE
        # =====================================================

        self.lbl_fase = ctk.CTkLabel(frame_formulario, text="Fase", width=75, anchor="w")
        self.lbl_fase.grid(row=8, column=0, sticky="w")

        opcoes_fase = [
            "Estudos Preliminares",
            "Projeto Básico",
            "Projeto Executivo"
        ]
        self.nm_fase = ctk.CTkOptionMenu(frame_formulario, values=opcoes_fase, command=self.carregar_scripts)
        self.nm_fase.grid(row=8, column=1, sticky="ew", padx=(10, 0), pady=2)
        self.nm_fase.set("Fase...")

        # =====================================================
        # VERSÃO DA ANÁLISE
        # =====================================================

        self.lbl_versao_analise = ctk.CTkLabel(frame_formulario, text="Versão da análise", width=75, anchor="w")
        self.lbl_versao_analise.grid(row=9, column=0, sticky="w")

        self.nm_versao_analise = ctk.CTkEntry(frame_formulario, placeholder_text="")
        self.nm_versao_analise.grid(row=9, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # NÚMERO DO ÚLTIMO RELATÓRIO
        # =====================================================

        self.lbl_numero_ult_rel = ctk.CTkLabel(frame_formulario, text="Número do último relatório", width=75, anchor="w")
        self.lbl_numero_ult_rel.grid(row=10, column=0, sticky="w")

        self.nm_numero_ult_rel = ctk.CTkEntry(frame_formulario, placeholder_text="")
        self.nm_numero_ult_rel.grid(row=10, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # ANALISTA
        # =====================================================

        self.lbl_analista = ctk.CTkLabel(frame_formulario, text="Analista", width=75, anchor="w")
        self.lbl_analista.grid(row=11, column=0, sticky="w")

        self.nm_analista = ctk.CTkEntry(frame_formulario, placeholder_text="")
        self.nm_analista.grid(row=11, column=1, sticky="ew", padx=(10, 0), pady=2)

    # =========================================================
    # LADO DIREITO
    # =========================================================

    def campos_lado_direito(self):

        # =====================================================
        # DIRETÓRIO PROJETO
        # =====================================================

        ctk.CTkButton(
            self.frame_direito,
            text="Selecione os arquivos para analisar",
            command=self.escolher_pdfs,
            width=320
        ).pack(pady=(25,2))

        self.lbl_arquivos_analise = ctk.CTkLabel(
            self.frame_direito,
            text="Nenhum arquivo selecionado",
            wraplength=350
        )

        self.lbl_arquivos_analise.pack(pady=(0, 15))

        # =====================================================
        # RESULTADOS
        # =====================================================

        ctk.CTkButton(
            self.frame_direito,
            text="Selecionar Diretório de Resultados",
            command=self.selecionar_dir_resultados,
            width=320
        ).pack(pady=2)

        self.lbl_dir_resultados = ctk.CTkLabel(
            self.frame_direito,
            text="Nenhum diretório selecionado",
            wraplength=350
        )

        self.lbl_dir_resultados.pack(pady=(0, 15))

        # =====================================================
        # RAP
        # =====================================================

        ctk.CTkButton(
            self.frame_direito,
            text="Selecionar Arquivo RAP",
            command=self.selecionar_rap,
            width=320
        ).pack(pady=2)

        self.label_rap = ctk.CTkLabel(
            self.frame_direito,
            text="Nenhum arquivo selecionado",
            wraplength=350
        )

        self.label_rap.pack(pady=(0, 15))

        # =====================================================
        # VERIFICAÇÕES POR DISCIPLINA
        # =====================================================

        self.label_script = ctk.CTkLabel(self.frame_direito, text="Selecione uma verificação")
        self.label_script.pack(pady=(20, 5))

        self.frame_verificacoes = ctk.CTkFrame(self.frame_direito, fg_color="transparent")
        self.frame_verificacoes.pack(fill="x", padx=90)
        self.frame_verificacoes.grid_columnconfigure(1, weight=1)

        self.lista_verificacoes = ctk.CTkOptionMenu(
            self.frame_verificacoes,
            values=[],
            width=320
        )
        self.lista_verificacoes.set("Selecione...")

        self.lista_verificacoes.grid(row=0, column=0, sticky="w", pady=2)

        # =====================================================
        # BOTÃO CARREGAR SCRIPTS
        # =====================================================

        #ctk.CTkButton(self.frame_verificacoes, text="Atualizar Scripts", command=self.carregar_scripts).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)

        # =====================================================
        # MENSAGEM DE ERRO
        # =====================================================

        self.label_error = ctk.CTkLabel(self.frame_direito, text="", fg_color="transparent") # texto alterado com a função selecionar_diretorio
        self.label_error.pack(anchor="center")

        # =====================================================
        # PROGRESSO
        # =====================================================

        self.progress = ctk.CTkProgressBar(
            self.frame_direito,
            mode="indeterminate"
        )

        # =====================================================
        # EXECUTAR
        # =====================================================

        self.btn_executar = ctk.CTkButton(
            self.frame_direito,
            text="Executar",
            command=self.executar_script,
            width=320,
            height=40
        )

        self.btn_executar.pack(pady=(80,0))


    # =========================================================
    # LADO INFERIOR
    # =========================================================

    def campos_inferior(self):
        self.btn_tema = ctk.CTkButton(
            self.frame_inferior,
            text="🌙 Modo Escuro",
            width=140,
            command=self.alternar_tema
        )

        self.btn_tema.pack(side="right", padx=10, pady=2)



    # =========================================================
    # DIRETÓRIOS
    # =========================================================

    def escolher_pdfs(self):
        arquivos = filedialog.askopenfilenames(
            title="Selecione os relatórios",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )

        if arquivos:
            salvar_json("arquivos-para-analisar", arquivos)

            nomes_arquivos = "\n".join(
                Path(arq).name
                for arq in arquivos
            )

            self.lbl_arquivos_analise.configure(text=nomes_arquivos, text_color=COR_TEXTO)


    def selecionar_dir_resultados(self):

        path = filedialog.askdirectory()

        if path:
            salvar_json("diretorio-resultados", path)

            self.lbl_dir_resultados.configure(text=path, text_color=COR_TEXTO)

    def selecionar_rap(self):

        path = filedialog.askopenfilename(
            title="Selecione um arquivo RAP",
            filetypes=[("Excel", "*.xlsx")]
        )

        if path:
            salvar_json("arquivo-rap", path)

            self.label_rap.configure(text=path, text_color=COR_TEXTO)

    # =========================================================
    # SCRIPTS
    # =========================================================

    def carregar_scripts(self, fase=None):
        fase = self.nm_fase.get()

        if fase == "Estudos Preliminares":
            pasta = caminho_arquivo(Path("checks") / "estudos")
        else:
            pasta = caminho_arquivo(Path("checks") / "projetos")

        try:
            scripts = sorted(
                f.name for f in pasta.iterdir()
                if f.is_file() and f.name.endswith(".py") and not f.name.startswith("_")
            )

        except Exception as e:
            print(f"Erro ao carregar scripts: {e}")
            scripts = []

        self.lista_verificacoes.configure(values=scripts)

        if scripts:
            self.lista_verificacoes.set(scripts[0])

    # =========================================================
    # MENSAGEM DE ERRO
    # =========================================================

    def limpar_validacao(self):
        labels = [
            self.lbl_processo,
            self.lbl_rodovia,
            self.lbl_extensao,
            self.lbl_lote,
            self.lbl_fase,
            self.lbl_analista,
            self.lbl_arquivos_analise,
            self.lbl_dir_resultados
        ]

        for label in labels:
            label.configure(text_color=COR_TEXTO)

        self.label_error.configure(text="")


    # =========================================================
    # VALIDAÇÃO
    # =========================================================

    def validar_campos(self):
        erro = False
        if not self.nm_processo.get().strip():
            self.lbl_processo.configure(text_color="red")
            erro = True

        if not self.nm_rodovia.get().strip():
            self.lbl_rodovia.configure(text_color="red")
            erro = True

        if not self.nm_extensao.get().strip():
            self.lbl_extensao.configure(text_color="red")
            erro = True

        if not self.nm_lote.get().strip():
            self.lbl_lote.configure(text_color="red")
            erro = True

        if self.nm_fase.get() == "Fase...":
            self.lbl_fase.configure(text_color="red")
            erro = True

        if not self.nm_analista.get().strip():
            self.lbl_analista.configure(text_color="red")
            erro = True

        if self.lbl_arquivos_analise.cget("text") == "Nenhum arquivo selecionado":
            self.lbl_arquivos_analise.configure(text_color="red")
            erro = True

        if self.lbl_dir_resultados.cget("text") == "Nenhum diretório selecionado":
            self.lbl_dir_resultados.configure(text_color="red")
            erro = True

        if erro:
            self.label_error.configure(
                text="Existem campos obrigatórios não preenchidos.",
                text_color="red"
            )

            self.after(
                8000,
                lambda: (
                    self.limpar_validacao()
                )
            )

            return

        br = self.nm_rodovia.get().strip()

        if not re.match(r"^\d{3}/[A-Z]{2}$", br):
            self.label_error.configure(
                text="BR inválida.\nUse XXX/UF",
                text_color="red"
            )

            return

        script = self.lista_verificacoes.get()
        if not script:
            self.label_error.configure(
                text="Selecione um script",
                text_color="red"
            )

            return
        return not erro

    # =========================================================
    # EXECUÇÃO
    # =========================================================

    def executar_script(self):
        if not self.validar_campos():
            return

        self.limpar_validacao()

        script = self.lista_verificacoes.get()
        fase = self.nm_fase.get()

        if fase == "Estudos Preliminares":
            pasta = caminho_arquivo(Path("checks") / "estudos")

        else:
            pasta = caminho_arquivo(Path("checks") / "projetos")

        script_path = pasta / script

        # =====================================================
        # SALVAR
        # =====================================================

        salvar_config({
            "processo": self.nm_processo.get(),
            "edital": self.nm_edital.get(),
            "contrato": self.nm_contrato.get(),
            "modalidade-de-contratacao":  self.nm_modalidade_de_contratacao.get(),
            "rodovia":  self.nm_rodovia.get(),
            "extensao":  self.nm_extensao.get(),
            "lote": fc.padronizar_lote( self.nm_lote.get()),
            "tipo-de-projeto": fc.padronizar_lote( self.nm_tipo_projeto.get()),
            "fase-de-projeto": fc.padronizar_lote( self.nm_fase.get()),
            "numero-analise": self.nm_versao_analise.get(),
            "numero-ult-relatorio": self.nm_numero_ult_rel.get(),
            "analista": self.nm_analista.get()
        })

        #print(self.nm_processo.get())

        # =====================================================
        # UI
        # =====================================================

        self.btn_executar.configure(
            state="disabled",
            text="Executando..."
        )

        self.progress.pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        self.progress.start()

        # =====================================================
        # THREAD
        # =====================================================

        def rodar():
            try:
                spec = importlib.util.spec_from_file_location(
                    "modulo_temp",
                    script_path
                    )
                
                modulo = importlib.util.module_from_spec(spec)

                spec.loader.exec_module(modulo)

                if hasattr(modulo, "main"):
                    modulo.main()

                self.after(
                    0,
                    lambda: self.label_error.configure(
                        text="Verificação concluída!",
                        text_color="green"
                        )
                    )

            except Exception as e:
                print(traceback.format_exc())

                self.after(
                    0,
                    lambda e=e: messagebox.showerror(
                        "Erro",
                        traceback.format_exc()
                    )
                )

            finally:
                self.after(
                    0,
                    self.progress.stop
                    )

                self.after(
                    0,
                    self.progress.pack_forget
                    )

                self.after(
                    0,
                    lambda: self.btn_executar.configure(
                        state="normal",
                        text="Executar"
                        )
                    )

        threading.Thread(target=rodar, daemon=True).start()


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    app = MainApp()

    # Esconde principal
    app.withdraw()

    # Splash
    splash = SplashScreen(app)

    # Loop único
    app.mainloop()