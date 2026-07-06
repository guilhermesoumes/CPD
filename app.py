"""Interface desktop para configurar e executar avaliações de completude."""

import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox
from pathlib import Path
import sys
import json
import threading
import importlib.util
import re
import scripts.funcoes_comuns as fc
import traceback

# =========================================================
# CONFIGURAÇÕES
# =========================================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COR_QUADRO = ("white", "#1f1f1f")
COR_TEXTO = ("black", "white")

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def caminho_arquivo(caminho_relativo):
    """Resolve arquivos do projeto no código-fonte ou no pacote PyInstaller."""

    caminho_base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return caminho_base / caminho_relativo

ARQUIVO_CONFIGURACAO = caminho_arquivo("config.json")

def salvar_json(chave, valor):
    """Atualiza uma única chave no arquivo local de configuração."""

    if Path(ARQUIVO_CONFIGURACAO).exists():
        with open(ARQUIVO_CONFIGURACAO, "r", encoding="utf-8") as arquivo_configuracao:
            dados = json.load(arquivo_configuracao)
    else:
        dados = {}

    dados[chave] = valor

    with open(ARQUIVO_CONFIGURACAO, "w", encoding="utf-8") as arquivo_configuracao:
        json.dump(dados, arquivo_configuracao, ensure_ascii=False, indent=4)


def salvar_config(dados_novos):
    """Mescla e persiste um conjunto de dados na configuração local."""

    dados = {}

    if Path(ARQUIVO_CONFIGURACAO).exists():
        with open(ARQUIVO_CONFIGURACAO, "r", encoding="utf-8") as arquivo_configuracao:
            dados = json.load(arquivo_configuracao)

    dados.update(dados_novos)

    with open(ARQUIVO_CONFIGURACAO, "w", encoding="utf-8") as arquivo_configuracao:
        json.dump(dados, arquivo_configuracao, ensure_ascii=False, indent=4)


def carregar_json():
    """Carrega a configuração local, se ela existir."""

    if Path(ARQUIVO_CONFIGURACAO).exists():

        with open(ARQUIVO_CONFIGURACAO, "r", encoding="utf-8") as arquivo_configuracao:
            return json.load(arquivo_configuracao)

    return {}

# =========================================================
# SPLASH SCREEN
# =========================================================

class TelaAbertura(ctk.CTkToplevel):
    """Exibe a identidade visual enquanto a janela principal é preparada."""

    def __init__(self, pai):
        """Inicializa e centraliza a tela de abertura."""

        super().__init__(pai)
        self.pai = pai

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

        rotulo_logo = ctk.CTkLabel(self,image=imagem,text="")
        rotulo_logo.pack()

        self.after(100, self.carregar)


    def carregar(self):
        """Agenda a conclusão da abertura após a preparação inicial."""

        # =====================================================
        # IMPORTS PESADOS
        # =====================================================

        self.after(1000, self.finalizar)


    def finalizar(self):
        """Fecha a abertura e revela a janela principal."""

        self.destroy()
        self.pai.deiconify()
    

# =========================================================
# APLICAÇÃO PRINCIPAL
# =========================================================

class AplicacaoPrincipal(ctk.CTk):
    """Janela principal de configuração e execução das verificações."""
    

    def __init__(self):
        """Configura a janela e restaura os dados da última execução."""

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
        """Preenche a interface com os valores persistidos em configuração."""
        dados = carregar_json()

        self.campo_processo.insert(0, dados.get("processo", ""))
        self.campo_edital.insert(0, dados.get("edital", ""))
        self.campo_contrato.insert(0, dados.get("contrato", ""))
        self.campo_modalidade_de_contratacao.insert(0, dados.get("modalidade-de-contratacao", ""))
        self.campo_rodovia.insert(0, dados.get("rodovia", ""))
        self.campo_extensao.insert(0, dados.get("extensao", ""))
        self.campo_lote.insert(0, dados.get("lote", ""))
        self.campo_versao_analise.insert(0, dados.get("numero-analise", ""))
        self.campo_numero_ult_rel.insert(0, dados.get("numero-ult-relatorio", ""))
        self.campo_analista.insert(0, dados.get("analista", ""))

        tipo_projeto = dados.get("tipo-de-projeto")
        if tipo_projeto:
            self.campo_tipo_projeto.set(tipo_projeto)

        fase = dados.get("fase-de-projeto")
        if fase:
            self.campo_fase.set(fase)
            self.carregar_verificacoes()
        
        arquivos = dados.get("arquivos-para-analisar")
        if arquivos:
            self.rotulo_arquivos_analise.configure(
                text="\n".join(Path(arquivo_salvo).name for arquivo_salvo in arquivos)
            )

        diretorio = dados.get("diretorio-resultados")
        if diretorio:
            self.rotulo_dir_resultados.configure(text=diretorio)

    # =========================================================
    # INTERFACE
    # =========================================================

    def criar_interface(self):
        """Cria e posiciona os quatro setores da interface."""

        # =====================================================
        # FRAME SUPERIOR
        # =====================================================

        self.quadro_superior = ctk.CTkFrame(self, fg_color=COR_QUADRO)

        self.quadro_superior.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        self.campos_superior()

        # =====================================================
        # FRAME ESQUERDO
        # =====================================================

        self.quadro_esquerdo = ctk.CTkFrame(self, fg_color=COR_QUADRO)

        self.quadro_esquerdo.place(relx=0, rely=0.1, relwidth=0.5, relheight=0.85)

        self.campos_lado_esquerdo()

        # =====================================================
        # FRAME DIREITO
        # =====================================================

        self.quadro_direito = ctk.CTkFrame(self, fg_color=COR_QUADRO)

        self.quadro_direito.place(relx=0.5, rely=0.1, relwidth=0.5, relheight=0.85)

        self.campos_lado_direito()

        # =====================================================
        # FRAME INFERIOR
        # =====================================================

        self.quadro_inferior = ctk.CTkFrame(self, fg_color=COR_QUADRO)

        self.quadro_inferior.place(relx=0, rely=0.95, relwidth=1, relheight=0.05)

        self.campos_inferior()

    # =========================================================
    # ALTERNAR MODO ESCURO E MODO CLARO
    # =========================================================

    def alternar_tema(self):
        """Alterna a aparência da aplicação entre os modos claro e escuro."""
        if self.tema_atual == "light":
            ctk.set_appearance_mode("dark")
            self.tema_atual = "dark"
            self.botao_tema.configure(text="☀️ Modo Claro")

        else:
            ctk.set_appearance_mode("light")
            self.tema_atual = "light"
            self.botao_tema.configure(text="🌙 Modo Escuro")

    # =========================================================
    # LADO SUPERIOR
    # =========================================================

    def campos_superior(self):
        """Monta o cabeçalho da aplicação."""
        
        # =====================================================
        # TÍTULO
        # =====================================================
        
        titulo = ctk.CTkLabel(self.quadro_superior, text="CPD-DNIT", font=("Arial", 28, "bold"), text_color="#223467")
        titulo.pack(pady=(20, 15))

    # =========================================================
    # LADO ESQUERDO
    # =========================================================

    def campos_lado_esquerdo(self):
        """Monta o formulário com os metadados do projeto."""

        # =====================================================
        # FRAME FORMULÁRIO
        # =====================================================
        quadro_formulario = ctk.CTkFrame(self.quadro_esquerdo, fg_color="transparent")
        quadro_formulario.pack(fill="x", padx=30, pady = (25,0))
        quadro_formulario.grid_columnconfigure(1, weight=1)


        # =====================================================
        # PROCESSO
        # =====================================================

        self.rotulo_processo = ctk.CTkLabel(quadro_formulario, text="Processo", width=75, anchor="w")
        self.rotulo_processo.grid(row=0, column=0, sticky="w", pady=2)

        self.campo_processo = ctk.CTkEntry(quadro_formulario)
        self.campo_processo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # EDITAL
        # =====================================================

        self.rotulo_edital = ctk.CTkLabel(quadro_formulario, text="Edital", width=75, anchor="w")
        self.rotulo_edital.grid(row=1, column=0, sticky="w")

        self.campo_edital = ctk.CTkEntry(quadro_formulario)
        self.campo_edital.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # CONTRATO
        # =====================================================

        self.rotulo_contrato = ctk.CTkLabel(quadro_formulario, text="Contrato", width=75, anchor="w")
        self.rotulo_contrato.grid(row=2, column=0, sticky="w")

        self.campo_contrato = ctk.CTkEntry(quadro_formulario)
        self.campo_contrato.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # MODALIDADE
        # =====================================================

        self.rotulo_modalidade = ctk.CTkLabel(quadro_formulario, text="Modalidade de contratação", width=75, anchor="w")
        self.rotulo_modalidade.grid(row=3, column=0, sticky="w")

        self.campo_modalidade_de_contratacao = ctk.CTkEntry(quadro_formulario)
        self.campo_modalidade_de_contratacao.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # BR
        # =====================================================

        self.rotulo_rodovia = ctk.CTkLabel(quadro_formulario, text="Rodovia", width=75, anchor="w")
        self.rotulo_rodovia.grid(row=4, column=0, sticky="w")

        self.campo_rodovia = ctk.CTkEntry(quadro_formulario, placeholder_text="BR no formato XXX/UF. Ex: 123/DF")
        self.campo_rodovia.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # EXTENSÃO
        # =====================================================

        self.rotulo_extensao = ctk.CTkLabel(quadro_formulario, text="Extensão", width=75, anchor="w")
        self.rotulo_extensao.grid(row=5, column=0, sticky="w")

        self.campo_extensao = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_extensao.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # LOTE
        # =====================================================

        self.rotulo_lote = ctk.CTkLabel(quadro_formulario, text="Lote", width=75, anchor="w")
        self.rotulo_lote.grid(row=6, column=0, sticky="w")

        self.campo_lote = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_lote.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # TIPO DE PROJETO
        # =====================================================

        self.rotulo_tipo_projeto = ctk.CTkLabel(quadro_formulario, text="Tipo de projeto", width=75, anchor="w")
        self.rotulo_tipo_projeto.grid(row=7, column=0, sticky="w")

        tipo_projeto = [
            "Duplicação",
            "Implantação",
            "Manutenção",
            "Misto",
            "OAE",
            "Proarte",
            "Reabilitação",
            "Restauração"
        ]
        self.campo_tipo_projeto = ctk.CTkOptionMenu(quadro_formulario, values=tipo_projeto)
        self.campo_tipo_projeto.grid(row=7, column=1, sticky="ew", padx=(10, 0), pady=2)
        self.campo_tipo_projeto.set("Tipo...")

        # =====================================================
        # FASE
        # =====================================================

        self.rotulo_fase = ctk.CTkLabel(quadro_formulario, text="Fase", width=75, anchor="w")
        self.rotulo_fase.grid(row=8, column=0, sticky="w")

        opcoes_fase = [
            "Estudos Preliminares",
            "Projeto Básico",
            "Projeto Executivo"
        ]
        self.campo_fase = ctk.CTkOptionMenu(quadro_formulario, values=opcoes_fase, command=self.carregar_verificacoes)
        self.campo_fase.grid(row=8, column=1, sticky="ew", padx=(10, 0), pady=2)
        self.campo_fase.set("Fase...")

        # =====================================================
        # VERSÃO DA ANÁLISE
        # =====================================================

        self.rotulo_versao_analise = ctk.CTkLabel(quadro_formulario, text="Versão da análise", width=75, anchor="w")
        self.rotulo_versao_analise.grid(row=9, column=0, sticky="w")

        self.campo_versao_analise = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_versao_analise.grid(row=9, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # NÚMERO DO ÚLTIMO RELATÓRIO
        # =====================================================

        self.rotulo_numero_ult_rel = ctk.CTkLabel(quadro_formulario, text="Número do último relatório", width=75, anchor="w")
        self.rotulo_numero_ult_rel.grid(row=10, column=0, sticky="w")

        self.campo_numero_ult_rel = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_numero_ult_rel.grid(row=10, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # ANALISTA
        # =====================================================

        self.rotulo_analista = ctk.CTkLabel(quadro_formulario, text="Analista", width=75, anchor="w")
        self.rotulo_analista.grid(row=11, column=0, sticky="w")

        self.campo_analista = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_analista.grid(row=11, column=1, sticky="ew", padx=(10, 0), pady=2)

    # =========================================================
    # LADO DIREITO
    # =========================================================

    def campos_lado_direito(self):
        """Monta os seletores de arquivos e os controles de execução."""

        # =====================================================
        # DIRETÓRIO PROJETO
        # =====================================================

        ctk.CTkButton(
            self.quadro_direito,
            text="Selecione os arquivos para analisar",
            command=self.escolher_pdfs,
            width=320
        ).pack(pady=(25,2))

        self.rotulo_arquivos_analise = ctk.CTkLabel(
            self.quadro_direito,
            text="Nenhum arquivo selecionado",
            wraplength=350
        )

        self.rotulo_arquivos_analise.pack(pady=(0, 15))

        # =====================================================
        # RESULTADOS
        # =====================================================

        ctk.CTkButton(
            self.quadro_direito,
            text="Selecionar Diretório de Resultados",
            command=self.selecionar_dir_resultados,
            width=320
        ).pack(pady=2)

        self.rotulo_dir_resultados = ctk.CTkLabel(
            self.quadro_direito,
            text="Nenhum diretório selecionado",
            wraplength=350
        )

        self.rotulo_dir_resultados.pack(pady=(0, 15))

        # =====================================================
        # VERIFICAÇÕES POR DISCIPLINA
        # =====================================================

        self.rotulo_verificacao = ctk.CTkLabel(self.quadro_direito, text="Selecione uma verificação")
        self.rotulo_verificacao.pack(pady=(20, 5))

        self.quadro_verificacoes = ctk.CTkFrame(self.quadro_direito, fg_color="transparent")
        self.quadro_verificacoes.pack(fill="x", padx=90)
        self.quadro_verificacoes.grid_columnconfigure(0, weight=1)

        self.lista_verificacoes = ctk.CTkOptionMenu(
            self.quadro_verificacoes,
            values=[],
            width=320
        )
        self.lista_verificacoes.set("Selecione...")

        self.lista_verificacoes.grid(row=0, column=0, pady=2)

        # =====================================================
        # MENSAGEM DE ERRO
        # =====================================================

        self.rotulo_erro = ctk.CTkLabel(self.quadro_direito, text="", fg_color="transparent") # texto alterado com a função selecionar_diretorio
        self.rotulo_erro.pack(anchor="center", pady=(0, 5))



        # =====================================================
        # EXECUTAR
        # =====================================================

        self.botao_executar = ctk.CTkButton(
            self.quadro_direito,
            text="Executar",
            command=self.executar_verificacao,
            width=320,
            height=40
        )

        self.botao_executar.pack(pady=(50,15))
        

        # =====================================================
        # PROGRESSO
        # =====================================================

        self.progresso = ctk.CTkProgressBar(
            self.quadro_direito,
            mode="indeterminate",
            width=320,
        )
        self.progresso.set(0)

        self.progresso.pack(pady=(5, 5))

        self.progresso.pack_forget()



    # =========================================================
    # LADO INFERIOR
    # =========================================================

    def campos_inferior(self):
        """Monta o rodapé e o controle de tema."""
        self.botao_tema = ctk.CTkButton(
            self.quadro_inferior,
            text="🌙 Modo Escuro",
            width=140,
            command=self.alternar_tema
        )

        self.botao_tema.pack(side="right", padx=10, pady=2)



    # =========================================================
    # DIRETÓRIOS
    # =========================================================

    def escolher_pdfs(self):
        """Seleciona e registra os relatórios PDF que serão analisados."""
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

            self.rotulo_arquivos_analise.configure(text=nomes_arquivos, text_color=COR_TEXTO)


    def selecionar_dir_resultados(self):
        """Seleciona o diretório onde os relatórios serão gravados."""

        caminho = filedialog.askdirectory()

        if caminho:
            salvar_json("diretorio-resultados", caminho)

            self.rotulo_dir_resultados.configure(text=caminho, text_color=COR_TEXTO)

    # =========================================================
    # SCRIPTS
    # =========================================================

    def carregar_verificacoes(self, fase=None):
        """Lista os módulos de verificação disponíveis para a fase escolhida."""
        fase = self.campo_fase.get()

        if fase == "Estudos Preliminares":
            pasta = caminho_arquivo(Path("checks") / "estudos")
        else:
            pasta = caminho_arquivo(Path("checks") / "projetos")

        try:
            verificacoes = sorted(
                arquivo.name for arquivo in pasta.iterdir()
                if arquivo.is_file() and arquivo.name.endswith(".py") and not arquivo.name.startswith("_")
            )

        except Exception as excecao:
            print(f"Erro ao carregar scripts: {excecao}")
            verificacoes = []

        self.lista_verificacoes.configure(values=verificacoes)

        if verificacoes:
            self.lista_verificacoes.set(verificacoes[0])

    # =========================================================
    # MENSAGEM DE ERRO
    # =========================================================

    def limpar_validacao(self):
        """Restaura a aparência dos campos após uma mensagem de validação."""
        rotulos = [
            self.rotulo_processo,
            self.rotulo_rodovia,
            self.rotulo_extensao,
            self.rotulo_lote,
            self.rotulo_fase,
            self.rotulo_analista,
            self.rotulo_arquivos_analise,
            self.rotulo_dir_resultados
        ]

        for rotulo in rotulos:
            rotulo.configure(text_color=COR_TEXTO)

        self.rotulo_erro.configure(text="")


    # =========================================================
    # VALIDAÇÃO
    # =========================================================

    def validar_campos(self):
        """Valida campos obrigatórios, rodovia e verificação selecionada."""
        erro = False
        if not self.campo_processo.get().strip():
            self.rotulo_processo.configure(text_color="red")
            erro = True

        if not self.campo_rodovia.get().strip():
            self.rotulo_rodovia.configure(text_color="red")
            erro = True

        if not self.campo_extensao.get().strip():
            self.rotulo_extensao.configure(text_color="red")
            erro = True

        if not self.campo_lote.get().strip():
            self.rotulo_lote.configure(text_color="red")
            erro = True

        if self.campo_fase.get() == "Fase...":
            self.rotulo_fase.configure(text_color="red")
            erro = True

        if not self.campo_analista.get().strip():
            self.rotulo_analista.configure(text_color="red")
            erro = True

        if self.rotulo_arquivos_analise.cget("text") == "Nenhum arquivo selecionado":
            self.rotulo_arquivos_analise.configure(text_color="red")
            erro = True

        if self.rotulo_dir_resultados.cget("text") == "Nenhum diretório selecionado":
            self.rotulo_dir_resultados.configure(text_color="red")
            erro = True

        if erro:
            self.rotulo_erro.configure(
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

        br = self.campo_rodovia.get().strip()

        if not re.match(r"^\d{3}/[A-Z]{2}$", br):
            self.rotulo_erro.configure(
                text="BR inválida.\nUse XXX/UF",
                text_color="red"
            )

            return

        nome_verificacao = self.lista_verificacoes.get()
        if not nome_verificacao:
            self.rotulo_erro.configure(
                text="Selecione um script",
                text_color="red"
            )

            return
        return not erro

    # =========================================================
    # EXECUÇÃO
    # =========================================================

    def executar_verificacao(self):
        """Persiste o formulário e executa a verificação em segundo plano."""
        if not self.validar_campos():
            return

        self.limpar_validacao()

        nome_verificacao = self.lista_verificacoes.get()
        fase = self.campo_fase.get()

        if fase == "Estudos Preliminares":
            pasta = caminho_arquivo(Path("checks") / "estudos")

        else:
            pasta = caminho_arquivo(Path("checks") / "projetos")

        caminho_verificacao = pasta / nome_verificacao

        # =====================================================
        # SALVAR
        # =====================================================

        salvar_config({
            "processo": self.campo_processo.get(),
            "edital": self.campo_edital.get(),
            "contrato": self.campo_contrato.get(),
            "modalidade-de-contratacao":  self.campo_modalidade_de_contratacao.get(),
            "rodovia":  self.campo_rodovia.get(),
            "extensao":  self.campo_extensao.get(),
            "lote": fc.padronizar_lote( self.campo_lote.get()),
            "tipo-de-projeto": (
                "" if self.campo_tipo_projeto.get() == "Tipo..."
                else fc.padronizar_lote(self.campo_tipo_projeto.get())),
            "fase-de-projeto": fc.padronizar_lote( self.campo_fase.get()),
            "numero-analise": self.campo_versao_analise.get(),
            "numero-ult-relatorio": self.campo_numero_ult_rel.get(),
            "analista": self.campo_analista.get()
        })

        # =====================================================
        # UI
        # =====================================================

        self.botao_executar.configure(
            state="disabled",
            text="Executando..."
        )

        self.progresso.pack(
            pady=(5, 5)
        )

        self.progresso.start()

        # =====================================================
        # THREAD
        # =====================================================

        def rodar():
            """Carrega o módulo selecionado e mantém a interface responsiva."""
            try:
                especificacao = importlib.util.spec_from_file_location(
                    "modulo_temp",
                    caminho_verificacao
                    )
                
                modulo = importlib.util.module_from_spec(especificacao)

                especificacao.loader.exec_module(modulo)

                if hasattr(modulo, "principal"):
                    modulo.principal()

                self.after(
                    0,
                    lambda: self.rotulo_erro.configure(
                        text="Verificação concluída!",
                        text_color="green"
                        )
                    )

            except Exception as excecao:
                print(traceback.format_exc())

                self.after(
                    0,
                    lambda excecao=excecao: messagebox.showerror(
                        "Erro",
                        traceback.format_exc()
                    )
                )

            finally:
                self.after(
                    0,
                    self.progresso.stop
                    )

                self.after(
                    0,
                    self.progresso.pack_forget
                    )

                self.after(
                    0,
                    lambda: self.botao_executar.configure(
                        state="normal",
                        text="Executar"
                        )
                    )

        threading.Thread(target=rodar, daemon=True).start()


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    aplicacao = AplicacaoPrincipal()

    # Esconde principal
    aplicacao.withdraw()

    # Splash
    tela_abertura = TelaAbertura(aplicacao)

    # Loop único
    aplicacao.mainloop()
