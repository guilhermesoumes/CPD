import re

def extrair_trechos_paginas(resposta: str):
    # Primeiro separa o item 2, como você já fazia
    lista_resposta = re.findall(
        r"\d+\s*\.\s*(.*?)(?=\n\d+\s*\.|$)",
        resposta,
        flags=re.S
    )

    if len(lista_resposta) < 2:
        return []

    resposta_item_2 = lista_resposta[-2]

    # Agora separa Trecho e Página
    padrao = re.compile(
        r"-\s*Trecho:\s*(?P<trecho>.*?)\s*,\s*na\s+página:\s*(?P<pagina>.*?)(?=\s*-\s*Trecho:|$)",
        flags=re.S | re.Iq
    )

    resultados = []

    for match in padrao.finditer(resposta_item_2):
        trecho = match.group("trecho").strip()
        pagina = match.group("pagina").strip()

        resultados.append({
            "trecho": trecho,
            "pagina": pagina
        })

    return resultados


resposta = """
1. Informação encontrada?
SIM

2. Trechos comprobatórios:
- Trecho: Esta classificação, de natureza técnica, relaciona-se diretamente com as características geométricas necessárias para atender seus objetivos: raios de curvatura, rampas, larguras de pista e acostamentos, distâncias de visibilidade, etc., na página: 14
- Trecho: Figura 8 - Seção Geométrica Típica de Ponte...44, na página: 5
- Trecho: Imagem 28 - Layout da Interseção em Nível 1...55, na página: 5

3. Conclusão:
SIM
"""

resposta_separada = extrair_trechos_paginas(resposta)