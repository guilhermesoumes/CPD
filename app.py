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
import scripts.executor_verificacoes as executor_verificacoes
import scripts.status_processamento as status_processamento
import traceback
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# =========================================================
# CONFIGURAÇÕES
# =========================================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COR_QUADRO = ("white", "#1f1f1f")
COR_TEXTO = ("black", "white")
COR_TITULO = ("#01356f", "#f7bf5d")

URL_LM_STUDIO = "http://127.0.0.1:1234/v1"
INTERVALO_VERIFICACAO_LM = 10_000  # milissegundos
TIMEOUT_VERIFICACAO_LM = 3  # segundos

ROTULOS_VERIFICACOES = {
    "estudo_geologico.py": "Estudo geológico",
    "estudo_geotecnico.py": "Estudo geotécnico",
    "estudo_hidrologico.py": "Estudo hidrológico",
    "estudo_tracado.py": "Estudo de traçado",
    "estudo_trafego.py": "Estudo de tráfego",
    "projeto_contencao.py": "Projeto de contenção",
    "projeto_geometrico.py": "Projeto geométrico",
    "projeto_obras_complementares.py": "Projeto de obras complementares",
    "projeto_pavimentacao.py": "Projeto de pavimentação",
    "projeto_sinalizacao.py": "Projeto de sinalização",
    "projeto_terraplanagem.py": "Projeto de terraplanagem",
}

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
ARQUIVO_CONFIGURACAO = fc.caminho_configuracao_usuario()


def caminho_arquivo(caminho_relativo):
    #Resolve arquivos do projeto no código-fonte ou no pacote PyInstaller.

    caminho_base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return caminho_base / caminho_relativo

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

def normalizar_contrato(contrato: str) -> str:
    """
    Padroniza o contrato para ser utilizado como chave no histórico.

    Assim, contratos digitados com diferenças de espaços ou letras
    minúsculas serão reconhecidos como o mesmo contrato.
    """
    return " ".join(contrato.strip().upper().split())

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
        self.geometry("1000x680")
        self.title("CPD-DNIT")
        self.resizable(True, True)
        self.processando = False
        self.cancelamento_evento = threading.Event()
        self.thread_execucao = None

        caminho_icone = caminho_arquivo(Path("figs") / "logo_icone.ico")
        self.iconbitmap(caminho_arquivo(caminho_icone))
        self.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        # =====================================================
        # INTERFACE
        # =====================================================
        self.processando = False
        self.cancelamento_evento = threading.Event()
        self.thread_execucao = None
        
        self.encerrando = False
        self.verificacao_lm_em_andamento = False
        self.agendamento_verificacao_lm = None
        self.lm_studio_conectado = False

        self.janela_sugestoes_contrato = None
        self.selecionando_sugestao_contrato = False
        self.arquivos_verificacao_por_rotulo = {}

        self.criar_interface()
        self.carregar_dados_salvos()

        self.verificar_conexao_lm_studio()

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
    # CONEXÃO LM STUDIO
    # =========================================================

    def consultar_lm_studio(self) -> tuple[bool, str]:
        """
        Consulta o endpoint de modelos do LM Studio.

        Retorna:
            tuple[bool, str]:
                - True quando o servidor respondeu corretamente.
                - False quando não foi possível estabelecer comunicação.
        """

        url_modelos = f"{URL_LM_STUDIO.rstrip('/')}/models"

        requisicao = Request(
            url_modelos,
            method="GET",
            headers={
                "Authorization": "Bearer lm-studio",
                "Accept": "application/json"
            }
        )

        try:
            with urlopen(
                requisicao,
                timeout=TIMEOUT_VERIFICACAO_LM
            ) as resposta:

                if 200 <= resposta.status < 300:
                    return True, "LM Studio conectado"

                return False, f"LM Studio respondeu com status {resposta.status}"

        except HTTPError as erro:
            # O servidor respondeu, mas houve um erro HTTP.
            return False, f"Erro HTTP do LM Studio: {erro.code}"

        except URLError:
            # Normalmente ocorre quando o LM Studio está fechado
            # ou o servidor local ainda não foi iniciado.
            return False, "LM Studio desconectado"

        except TimeoutError:
            return False, "Tempo de conexão esgotado"

        except Exception as erro:
            print(f"Erro ao verificar LM Studio: {erro}")
            return False, "Erro ao verificar LM Studio"


    def verificar_conexao_lm_studio(self):
        """
        Inicia uma verificação em segundo plano.

        Esse método não bloqueia a interface gráfica.
        """

        if self.encerrando:
            return

        # Impede duas verificações simultâneas.
        if self.verificacao_lm_em_andamento:
            return

        self.verificacao_lm_em_andamento = True

        self.rotulo_status_lm.configure(
            text="● Verificando conexão com o LM Studio...",
            text_color="#d97706"
        )

        def executar_verificacao():
            conectado, mensagem = self.consultar_lm_studio()

            if self.encerrando:
                return

            self.after(
                0,
                lambda: self.atualizar_status_lm(
                    conectado,
                    mensagem
                )
            )

        threading.Thread(
            target=executar_verificacao,
            daemon=True
        ).start()


    def atualizar_status_lm(self, conectado: bool, mensagem: str):
        """Atualiza visualmente o indicador de conexão."""

        self.verificacao_lm_em_andamento = False
        self.lm_studio_conectado = conectado

        if self.encerrando:
            return

        if conectado:
            self.rotulo_status_lm.configure(
                text=f"● {mensagem}",
                text_color="#16a34a"
            )
        else:
            self.rotulo_status_lm.configure(
                text=f"● {mensagem}",
                text_color="#dc2626"
            )

        # Agenda uma nova verificação.
        self.agendamento_verificacao_lm = self.after(
            INTERVALO_VERIFICACAO_LM,
            self.verificar_conexao_lm_studio
        )

    # =========================================================
    # AUTOCOMPLETE CONTRATO
    # =========================================================
    def obter_contratos_salvos(self) -> list[str]:
        """Retorna os contratos armazenados no histórico."""
        dados = carregar_json()
        historico = dados.get("historico-contratos", {})

        return sorted(historico.keys())


    def atualizar_sugestoes_contrato(self, *_args) -> None:
        """
        Mostra contratos salvos que correspondem ao texto digitado.
        """
        texto_digitado = normalizar_contrato(
            self.variavel_contrato.get()
        )

        if not texto_digitado:
            self.fechar_sugestoes_contrato()
            return

        contratos = self.obter_contratos_salvos()

        sugestoes = [
            contrato
            for contrato in contratos
            if texto_digitado in contrato
        ]

        # Evita mostrar a lista quando o contrato já foi digitado por completo.
        if not sugestoes or sugestoes == [texto_digitado]:
            self.fechar_sugestoes_contrato()
            return

        self.mostrar_sugestoes_contrato(sugestoes[:8])


    def mostrar_sugestoes_contrato(
        self,
        sugestoes: list[str]
    ) -> None:
        """Exibe as sugestões abaixo do campo Contrato."""
        self.fechar_sugestoes_contrato()

        self.update_idletasks()

        x = self.campo_contrato.winfo_rootx()
        y = (
            self.campo_contrato.winfo_rooty()
            + self.campo_contrato.winfo_height()
        )

        largura = self.campo_contrato.winfo_width()
        altura = min(len(sugestoes) * 36, 250)

        self.janela_sugestoes_contrato = ctk.CTkToplevel(self)
        self.janela_sugestoes_contrato.overrideredirect(True)
        self.janela_sugestoes_contrato.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )

        self.janela_sugestoes_contrato.attributes("-topmost", True)

        quadro = ctk.CTkScrollableFrame(
            self.janela_sugestoes_contrato,
            corner_radius=4
        )
        quadro.pack(fill="both", expand=True)

        for contrato in sugestoes:
            botao = ctk.CTkButton(
                quadro,
                text=contrato,
                anchor="w",
                height=30,
                fg_color="transparent",
                text_color=COR_TEXTO,
                hover_color=("#d9d9d9", "#333333"),
                command=lambda valor=contrato: (
                    self.selecionar_contrato_sugerido(valor)
                )
            )

            botao.pack(
                fill="x",
                padx=2,
                pady=1
            )


    def selecionar_contrato_sugerido(
        self,
        contrato: str
    ) -> None:
        """Insere o contrato selecionado e recupera seus dados."""
        self.selecionando_sugestao_contrato = True

        self.variavel_contrato.set(contrato)
        self.fechar_sugestoes_contrato()

        self.buscar_dados_do_contrato()

        self.campo_contrato.focus_set()
        self.campo_contrato.icursor("end")

        self.after(
            100,
            self.finalizar_selecao_sugestao
        )


    def finalizar_selecao_sugestao(self) -> None:
        self.selecionando_sugestao_contrato = False


    def ao_sair_campo_contrato(self, evento=None) -> None:
        """
        Aguarda brevemente antes de fechar a lista.

        Esse atraso permite que o clique em uma sugestão seja processado.
        """
        self.after(
            150,
            self.processar_saida_campo_contrato
        )


    def processar_saida_campo_contrato(self) -> None:
        if self.selecionando_sugestao_contrato:
            return

        self.fechar_sugestoes_contrato()
        self.buscar_dados_do_contrato()


    def fechar_sugestoes_contrato(self) -> None:
        """Fecha a janela de sugestões, caso esteja aberta."""
        if self.janela_sugestoes_contrato is not None:
            try:
                self.janela_sugestoes_contrato.destroy()
            except Exception:
                pass

            self.janela_sugestoes_contrato = None

    
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
        
        titulo = ctk.CTkLabel(self.quadro_superior, text="CPD-DNIT", font=("Arial", 40, "bold"), text_color=COR_TITULO)
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
        # CONTRATO
        # =====================================================

        self.rotulo_contrato = ctk.CTkLabel(quadro_formulario, text="Contrato", width=75, anchor="w")
        self.rotulo_contrato.grid(row=0, column=0, sticky="w")

        self.variavel_contrato = ctk.StringVar()
        self.campo_contrato = ctk.CTkEntry(
            quadro_formulario,
            textvariable=self.variavel_contrato
        )

        self.campo_contrato.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)

        self.variavel_contrato.trace_add(
            "write",
            self.atualizar_sugestoes_contrato
        )

        self.campo_contrato.bind(
            "<FocusOut>",
            self.ao_sair_campo_contrato
        )

        self.campo_contrato.bind(
            "<Return>",
            self.buscar_dados_do_contrato
        )

        self.campo_contrato.bind(
            "<FocusOut>",
            self.buscar_dados_do_contrato
        )

        self.campo_contrato.bind(
            "<Return>",
            self.buscar_dados_do_contrato
        )

        # =====================================================
        # PROCESSO
        # =====================================================

        self.rotulo_processo = ctk.CTkLabel(quadro_formulario, text="*Processo", width=75, anchor="w")
        self.rotulo_processo.grid(row=1, column=0, sticky="w", pady=2)

        self.campo_processo = ctk.CTkEntry(quadro_formulario)
        self.campo_processo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # EDITAL
        # =====================================================

        self.rotulo_edital = ctk.CTkLabel(quadro_formulario, text="Edital", width=75, anchor="w")
        self.rotulo_edital.grid(row=2, column=0, sticky="w")

        self.campo_edital = ctk.CTkEntry(quadro_formulario)
        self.campo_edital.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)

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

        self.rotulo_rodovia = ctk.CTkLabel(quadro_formulario, text="*Rodovia", width=75, anchor="w")
        self.rotulo_rodovia.grid(row=4, column=0, sticky="w")

        self.campo_rodovia = ctk.CTkEntry(quadro_formulario, placeholder_text="BR no formato XXX/UF. Ex: 123/DF")
        self.campo_rodovia.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # SEGMENTO
        # =====================================================

        self.rotulo_segmento = ctk.CTkLabel(quadro_formulario, text="Segmento", width=75, anchor="w")
        self.rotulo_segmento.grid(row=5, column=0, sticky="w")

        self.campo_segmento = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_segmento.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # EXTENSÃO
        # =====================================================

        self.rotulo_extensao = ctk.CTkLabel(quadro_formulario, text="*Extensão", width=75, anchor="w")
        self.rotulo_extensao.grid(row=6, column=0, sticky="w")

        self.campo_extensao = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_extensao.grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # LOTE
        # =====================================================

        self.rotulo_lote = ctk.CTkLabel(quadro_formulario, text="*Lote", width=75, anchor="w")
        self.rotulo_lote.grid(row=7, column=0, sticky="w")

        self.campo_lote = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_lote.grid(row=7, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # TIPO DE PROJETO
        # =====================================================

        self.rotulo_tipo_projeto = ctk.CTkLabel(quadro_formulario, text="Tipo de projeto", width=75, anchor="w")
        self.rotulo_tipo_projeto.grid(row=8, column=0, sticky="w")

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
        self.campo_tipo_projeto.grid(row=8, column=1, sticky="ew", padx=(10, 0), pady=2)
        self.campo_tipo_projeto.set("Tipo...")

        # =====================================================
        # FASE
        # =====================================================

        self.rotulo_fase = ctk.CTkLabel(quadro_formulario, text="*Fase", width=75, anchor="w")
        self.rotulo_fase.grid(row=9, column=0, sticky="w")

        opcoes_fase = [
            "Estudos Preliminares",
            "Projeto Básico",
            "Projeto Executivo"
        ]
        self.campo_fase = ctk.CTkOptionMenu(quadro_formulario, values=opcoes_fase, command=self.carregar_verificacoes)
        self.campo_fase.grid(row=9, column=1, sticky="ew", padx=(10, 0), pady=2)
        self.campo_fase.set("Fase...")

        # =====================================================
        # VERSÃO DA ANÁLISE
        # =====================================================

        self.rotulo_versao_analise = ctk.CTkLabel(quadro_formulario, text="Versão da análise", width=75, anchor="w")
        self.rotulo_versao_analise.grid(row=10, column=0, sticky="w")

        self.campo_versao_analise = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_versao_analise.grid(row=10, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # NÚMERO DO ÚLTIMO RELATÓRIO
        # =====================================================

        self.rotulo_numero_ult_rel = ctk.CTkLabel(quadro_formulario, text="Número do último relatório", width=75, anchor="w")
        self.rotulo_numero_ult_rel.grid(row=11, column=0, sticky="w")

        self.campo_numero_ult_rel = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_numero_ult_rel.grid(row=11, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # ANALISTA
        # =====================================================

        self.rotulo_analista = ctk.CTkLabel(quadro_formulario, text="*Analista", width=75, anchor="w")
        self.rotulo_analista.grid(row=12, column=0, sticky="w")

        self.campo_analista = ctk.CTkEntry(quadro_formulario, placeholder_text="")
        self.campo_analista.grid(row=12, column=1, sticky="ew", padx=(10, 0), pady=2)

        # =====================================================
        # MENSAGEM CAMPOS OBRIGATÓRIOS
        # =====================================================

        self.mensagem_campos_obrigatorios = ctk.CTkLabel(
            self.quadro_esquerdo,
            text="* Campos obrigatórios",
            wraplength=350,
            anchor="w",
        )

        self.mensagem_campos_obrigatorios.pack(
            fill="x",
            padx=35,
            pady=(30, 10)
        )

        # =====================================================
        # BOTÃO LIMPAR CAMPOS
        # =====================================================

        self.botao_limpar = ctk.CTkButton(
            self.quadro_esquerdo,
            text="Limpar campos",
            command=self.limpar_campos,
            width=320
        ).pack(pady=(30,2))

    # =========================================================
    # LADO DIREITO
    # =========================================================

    def campos_lado_direito(self):
        """Monta os seletores de arquivos e os controles de execução."""

        # =====================================================
        # ARQUIVOS PARA ANÁLISE
        # =====================================================

        ctk.CTkButton(
            self.quadro_direito,
            text="*Selecione os arquivos para analisar",
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
            text="*Selecionar Diretório de Resultados",
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
            command=self.acao_botao_executar,
            width=320,
            height=40
        )

        self.botao_executar.pack(pady=(50,15))

        self.campo_status = ctk.CTkTextbox(
            self.quadro_direito,
            width=420,
            height=115,
            wrap="word",
            state="disabled",
        )
        self.campo_status.pack(pady=(0, 5), padx=20, fill="x")
        self.atualizar_status_processamento({
            "etapa": "Aguardando",
            "mensagem": "Preencha os dados e clique em Executar.",
        })
        

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
        self.rotulo_status_lm = ctk.CTkLabel(
            self.quadro_inferior,
            text="● Verificando conexão com o LM Studio...",
            text_color="#d97706",
            font=("Arial", 12)
        )

        self.rotulo_status_lm.pack(
            side="left",
            padx=15,
            pady=2
        )
        
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
    # CARREGAR VERIFICAÇÕES
    # =========================================================

    def carregar_verificacoes(self, fase=None):
        """Lista os módulos de verificação disponíveis para a fase escolhida."""
        fase = self.campo_fase.get()

        if fase == "Estudos Preliminares":
            pasta = caminho_arquivo(Path("checks") / "estudos")
        else:
            pasta = caminho_arquivo(Path("checks") / "projetos")

        try:
            arquivos_verificacao = sorted(
                arquivo.name for arquivo in pasta.iterdir()
                if arquivo.is_file() and arquivo.name.endswith(".py") and not arquivo.name.startswith("_")
            )

        except Exception as excecao:
            print(f"Erro ao carregar scripts: {excecao}")
            arquivos_verificacao = []

        self.arquivos_verificacao_por_rotulo = {
            ROTULOS_VERIFICACOES.get(
                nome_arquivo,
                Path(nome_arquivo).stem.replace("_", " ").capitalize(),
            ): nome_arquivo
            for nome_arquivo in arquivos_verificacao
        }
        rotulos = list(self.arquivos_verificacao_por_rotulo)

        self.lista_verificacoes.configure(values=rotulos)

        if rotulos:
            self.lista_verificacoes.set(rotulos[0])
        else:
            self.lista_verificacoes.set("Selecione...")

    # =========================================================
    # MENSAGEM DE ERRO
    # =========================================================

    def limpar_validacao(self):
        """Restaura a aparência dos campos após uma mensagem de validação."""
        rotulos = [
            self.rotulo_processo,
            self.rotulo_rodovia,
            self.rotulo_segmento,
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

        rotulo_verificacao = self.lista_verificacoes.get()
        if rotulo_verificacao not in self.arquivos_verificacao_por_rotulo:
            self.rotulo_erro.configure(
                text="Selecione uma verificação",
                text_color="red"
            )

            return
        return not erro

    # =========================================================
    # SALVAR CAMPOS CONTRATO, PROCESSO E EDITAL
    # =========================================================

    def preencher_campo(self, campo: ctk.CTkEntry, valor: str) -> None:
        """Substitui o conteúdo atual de um campo."""
        campo.delete(0, "end")
        campo.insert(0, valor)


    def buscar_dados_do_contrato(self, evento=None) -> None:
        """
        Busca Processo e Edital associados ao contrato informado.

        Os campos continuam sendo CTkEntry comuns e permanecem editáveis.
        """
        contrato = normalizar_contrato(self.campo_contrato.get())

        if not contrato:
            return

        dados = carregar_json()
        historico = dados.get("historico-contratos", {})

        dados_contrato = historico.get(contrato)

        if dados_contrato is None:
            # O contrato ainda não está registrado.
            # Limpa os dados referentes ao contrato anterior.
            self.preencher_campo(self.campo_processo, "")
            self.preencher_campo(self.campo_edital, "")
            return

        self.preencher_campo(
            self.campo_processo,
            dados_contrato.get("processo", "")
        )

        self.preencher_campo(
            self.campo_edital,
            dados_contrato.get("edital", "")
        )


    def salvar_historico_contrato(self) -> None:
        """
        Salva ou atualiza Processo e Edital vinculados ao contrato atual.
        """
        contrato = normalizar_contrato(self.campo_contrato.get())

        if not contrato:
            return

        processo = self.campo_processo.get().strip()
        edital = self.campo_edital.get().strip()

        dados = carregar_json()
        historico = dados.get("historico-contratos", {})

        historico[contrato] = {
            "processo": processo,
            "edital": edital
        }

        salvar_config({
            "historico-contratos": historico
        })

    # =========================================================
    # LIMPAR CAMPOS
    # =========================================================

    def limpar_campos(self):
        """Limpa todos os campos e seleções preenchidos na interface."""

        if self.processando:
            messagebox.showwarning(
                "Operação em andamento",
                "Não é possível limpar os campos durante o processamento."
            )
            return

        confirmar = messagebox.askyesno(
            "Limpar campos",
            "Deseja realmente limpar todos os campos preenchidos?"
        )

        if not confirmar:
            return

        # Fecha a janela de sugestões do contrato, caso esteja aberta.
        self.fechar_sugestoes_contrato()

        # Campos de texto.
        campos_texto = [
            self.campo_contrato,
            self.campo_processo,
            self.campo_edital,
            self.campo_modalidade_de_contratacao,
            self.campo_rodovia,
            self.campo_segmento,
            self.campo_extensao,
            self.campo_lote,
            self.campo_versao_analise,
            self.campo_numero_ult_rel,
            self.campo_analista
        ]

        for campo in campos_texto:
            campo.delete(0, "end")

        # Menus de seleção.
        self.campo_tipo_projeto.set("Tipo...")
        self.campo_fase.set("Fase...")
        self.lista_verificacoes.configure(values=[])
        self.lista_verificacoes.set("Selecione...")
        self.arquivos_verificacao_por_rotulo = {}

        # Arquivos e diretório selecionados.
        self.rotulo_arquivos_analise.configure(
            text="Nenhum arquivo selecionado",
            text_color=COR_TEXTO
        )

        self.rotulo_dir_resultados.configure(
            text="Nenhum diretório selecionado",
            text_color=COR_TEXTO
        )

        # Remove mensagens e destaques de validação.
        self.limpar_validacao()

        # Retorna o cursor ao primeiro campo.
        self.campo_contrato.focus_set()

    # =========================================================
    # EXECUÇÃO
    # =========================================================

    def atualizar_status_processamento(self, evento: dict) -> None:
        """Mostra o evento mais recente no painel de acompanhamento."""
        linhas = [
            f"Etapa: {evento.get('etapa', '-')}",
            f"Status: {evento.get('mensagem', '-')}",
        ]
        if evento.get("arquivo"):
            linhas.append(f"Arquivo: {evento['arquivo']}")
        if evento.get("pagina") and evento.get("total_paginas"):
            linhas.append(f"Página: {evento['pagina']} de {evento['total_paginas']}")
        elif evento.get("pagina"):
            linhas.append(f"Página: {evento['pagina']}")
        if evento.get("perguntas_concluidas") is not None:
            linhas.append(
                f"Perguntas concluídas: {evento['perguntas_concluidas']} de "
                f"{evento.get('total_perguntas', '?')}"
            )

        self.campo_status.configure(state="normal")
        self.campo_status.delete("1.0", "end")
        self.campo_status.insert("1.0", "\n".join(linhas))
        self.campo_status.configure(state="disabled")


    def receber_status_processamento(self, evento: dict) -> None:
        """Agenda na thread gráfica uma atualização recebida do processamento."""
        self.after(0, lambda evento=evento: self.atualizar_status_processamento(evento))


    def acao_botao_executar(self):
        """Executa a verificacao ou solicita a interrupcao do processamento."""
        if self.processando:
            self.solicitar_interrupcao()
            return

        self.executar_verificacao()


    def solicitar_interrupcao(self):
        """Sinaliza ao RAG que a execucao deve parar assim que possivel."""
        self.cancelamento_evento.set()
        self.atualizar_status_processamento({
            "etapa": "Interrupção",
            "mensagem": "Aguardando a operação atual terminar com segurança...",
        })
        self.botao_executar.configure(
            state="disabled",
            text="Interrompendo..."
        )
        self.rotulo_erro.configure(
            text="Interrompendo processamento...",
            text_color="orange"
        )


    def executar_verificacao(self):
        """Persiste o formulário e executa a verificação em segundo plano."""
        if not self.lm_studio_conectado:
            self.atualizar_status_processamento({
                "etapa": "LM Studio desconectado",
                "mensagem": (
                    "Abra o LM Studio e inicie o servidor local para continuar. "
                    "Depois, tente executar novamente."
                ),
            })
            self.rotulo_erro.configure(
                text="É necessário abrir o LM Studio para executar a verificação.",
                text_color="red",
            )
            self.verificar_conexao_lm_studio()
            return

        if not self.validar_campos():
            return

        self.salvar_historico_contrato()
        
        self.limpar_validacao()
        self.cancelamento_evento.clear()
        self.processando = True
        executor_verificacoes.definir_cancelamento_evento(self.cancelamento_evento)
        status_processamento.definir_callback(self.receber_status_processamento)
        self.atualizar_status_processamento({
            "etapa": "Iniciando",
            "mensagem": "Carregando a verificação selecionada...",
        })

        rotulo_verificacao = self.lista_verificacoes.get()
        nome_verificacao = self.arquivos_verificacao_por_rotulo[rotulo_verificacao]
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
            "contrato": self.campo_contrato.get(),
            "processo": self.campo_processo.get(),
            "edital": self.campo_edital.get(),
            "modalidade-de-contratacao":  self.campo_modalidade_de_contratacao.get(),
            "rodovia":  self.campo_rodovia.get(),
            "segmento":  self.campo_segmento.get(),
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
            state="normal",
            text="Interromper"
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

                self.receber_status_processamento({
                    "etapa": "Concluído",
                    "mensagem": "Todos os arquivos foram processados.",
                })
                self.after(
                    0,
                    lambda: self.rotulo_erro.configure(
                        text="Verificação concluída!",
                        text_color="green"
                        )
                    )

            except fc.ProcessamentoInterrompido:
                self.receber_status_processamento({
                    "etapa": "Interrompido",
                    "mensagem": "O processamento foi interrompido pelo usuário.",
                })
                self.after(
                    0,
                    lambda: self.rotulo_erro.configure(
                        text="Processamento interrompido.",
                        text_color="orange"
                        )
                    )

            except Exception as excecao:
                print(traceback.format_exc())
                self.receber_status_processamento({
                    "etapa": "Erro",
                    "mensagem": str(excecao),
                })

                self.after(
                    0,
                    lambda excecao=excecao: messagebox.showerror(
                        "Erro",
                        traceback.format_exc()
                    )
                )

            finally:
                executor_verificacoes.definir_cancelamento_evento(None)
                status_processamento.definir_callback(None)
                self.processando = False

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

        self.thread_execucao = threading.Thread(target=rodar, daemon=True)
        self.thread_execucao.start()


    def ao_fechar(self):
        self.encerrando = True

        if self.agendamento_verificacao_lm is not None:
            try:
                self.after_cancel(self.agendamento_verificacao_lm)
            except Exception:
                pass

            self.agendamento_verificacao_lm = None

        if self.processando:
            self.cancelamento_evento.set()

        executor_verificacoes.definir_cancelamento_evento(None)

        try:
            fc.descarregar_modelos_carregados()
        except Exception as erro:
            print(f"Erro ao descarregar modelos: {erro}")

        self.destroy()


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
