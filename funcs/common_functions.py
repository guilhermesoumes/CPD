import os
import re
import sys
import unicodedata
from pathlib import Path
import json

def resource_path(relative_path):
    #Retorna o caminho absoluto para um recurso, mesmo quando empacotado em .exe
    if hasattr(sys, '_MEIPASS'):  # atributo criado pelo PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_info(CONFIG_FILE, info): # Pega uma informação genérica salva no json
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados.get(info)
    return None

def load_config(config_file: str) -> dict:
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Cria os caminhos dos subdiretórios de saída dos relatórios
def ensure_output_dirs(folder: str):
    os.makedirs(folder, exist_ok=True)

# Procura por um arquivo "RAP.xlsx" numa pasta
def path_rap_excel(pasta: str) -> str:
    try:
        for nome in os.listdir(pasta):
            if nome.lower().endswith(".xlsx") and nome.lower().startswith("rap"):
                return os.path.join(pasta, nome)
    except FileNotFoundError:
        pass
    return ""

# Normaliza uma string, simplificando e padronizando o texto
def norm(s: str) -> str:
    s = "" if s is None else str(s) # Se s for None, vira "" (string vazia)
    s_nfkd = unicodedata.normalize("NFKD", s) # Decompõe caracteres acentuados em letra base + acento separado
    s_ascii = "".join(ch for ch in s_nfkd if not unicodedata.combining(ch)) # Remove acentos e sinais de combinação. ex: "ação" -> "acao"
    return s_ascii.strip().lower() # remove espaços do início e do fim, e converte tudo para minúsculas

# Gera texto para relatório excel
def classificar_status(status_texto: str):
    s = norm(status_texto)
    if "reprovado" in s:
        return ("-", "-", "✖")
    if "aprovado" in s and "ressalva" in s:
        return ("-", "⚠️", "-")
    if "aprovado" in s and "ressalva" not in s:
        return ("✔", "-", "-")
    return ("-", "-", "-")

def truefalse_to_vx(status_texto: str):
    if status_texto == False:
        return "✖"
    elif status_texto == True:
        return "✔"
    else:
        return status_texto
    
# Descobrir e retornar o caminho do arquivo de template .xlsx mais recente dentro de uma pasta específica.
def resolver_template(PATH_TEMPLATE_DIR):
    if os.path.isdir(PATH_TEMPLATE_DIR):
        candidatos = []
        for f in os.listdir(PATH_TEMPLATE_DIR):
            if f.lower().endswith("verificacao.xlsx"):
                candidatos.append(os.path.join(PATH_TEMPLATE_DIR, f))
        if candidatos:
            candidatos.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            return candidatos[0]
    return ""

# Descobrir e retornar o caminho do arquivo de template .xlsx mais recente dentro de uma pasta específica.
def resolver_template_estudos(PATH_TEMPLATE_DIR):
    if os.path.isdir(PATH_TEMPLATE_DIR):
        candidatos = []
        for f in os.listdir(PATH_TEMPLATE_DIR):
            if f.lower().endswith("estudos.xlsx"):
                candidatos.append(os.path.join(PATH_TEMPLATE_DIR, f))
        if candidatos:
            candidatos.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            return candidatos[0]
    return ""

def prox_versao_pasta(dir_saida: str, base_nome: str) -> tuple[str, str]:
    #pastas_existentes = os.listdir(dir_saida)
    pastas_existentes = [entrada.name for entrada in os.scandir(dir_saida) if entrada.is_dir()]
    padrao = re.compile(rf"_V(\d{{2}})", re.IGNORECASE)
    versoes = [int(m.group(1)) for f in pastas_existentes if (m := padrao.match(f))]
    nova_versao = max(versoes) + 1 if versoes else 1
    nome = f"-V{nova_versao:02d}.xlsx"
    caminho = os.path.join(dir_saida, nome)
    return nome, caminho

# Verifica se na pasta tem certas extensões de arquivos
def exists_file_with_ext(directory: Path, extensions: tuple[str, ...]) -> bool:
    if not directory.exists():
        return False
    return any(file.suffix.lower() in extensions for file in directory.iterdir() if file.is_file())

def padronizar_lote(s: str) -> str:
    s = str(s)
    # Tenta separar número (um ou mais dígitos) + opcional letra
    match = re.match(r"^(\d+)([A-Za-z]?)$", s)
    if match:
        numero, letra = match.groups()
        return numero.zfill(2) + letra.upper()
    else:
        # Caso não bata com o padrão (ex: strings estranhas), retorna como está
        return s
    
def prox_versao(dir_saida: str, ano, br: str, disciplina, lote: str) -> str:
    # Monta o nome-base sem a parte da versão
    base_nome = f"RAC-000-{ano}_BR-{br}_{disciplina}_LT-{lote}"

    # Expressão regular que encontra a parte "RAC_0012025_BR-01_PGMT_LT-02", por exemplo
    padrao = re.compile(rf"RAC-(\d{{3}})-{ano}_BR-{re.escape(br)}_{re.escape(disciplina)}_LT-{re.escape(lote)}", re.IGNORECASE)

    # Procura pastas existentes que sigam o padrão
    if not os.path.isdir(dir_saida):
        os.makedirs(dir_saida, exist_ok=True)
    pastas_existentes = [entrada.name for entrada in os.scandir(dir_saida) if entrada.is_file()]

    # Extrai números de versão existentes
    versoes = [int(m.group(1)) for f in pastas_existentes if (m := padrao.match(f))]

    # Define a nova versão
    nova_versao = max(versoes) + 1 if versoes else 1

    # Substitui "XXX" pela nova versão
    nome = base_nome.replace("000", f"{nova_versao:03d}")
    return nome



