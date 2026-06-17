from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, LongTable, Paragraph

import os
import funcs.common_functions as fc
from datetime import datetime
import re
from xml.sax.saxutils import escape


CONFIG_FILE = fc.resource_path("config.json") # Arquivo com informações do projeto

fase = fc.get_info(CONFIG_FILE, "fase-de-projeto")
rodovia = fc.get_info(CONFIG_FILE, "rodovia")
lote = fc.get_info(CONFIG_FILE, "lote")
dic_pr = fc.get_info(CONFIG_FILE, "processo")
dic_ed = fc.get_info(CONFIG_FILE, "edital")
dic_co = fc.get_info(CONFIG_FILE, "contrato")
dic_mo = fc.get_info(CONFIG_FILE, "modalidade-de-contratacao")
dic_ro = fc.get_info(CONFIG_FILE, "rodovia")
dic_ex = fc.get_info(CONFIG_FILE, "extensao")
dic_lo = lote
dic_tp = fc.get_info(CONFIG_FILE, "tipo-de-projeto")
dic_fa = fc.get_info(CONFIG_FILE, "fase-de-projeto")
dic_na = fc.get_info(CONFIG_FILE, "numero-analise")
dic_nr = fc.get_info(CONFIG_FILE, "numero-ult-relatorio")
dic_an = fc.get_info(CONFIG_FILE, "analista")
data_str = datetime.now().strftime("%d/%m/%Y")
hora_str = datetime.now().strftime("%H:%M")

global page
page = 1

def gerar_pdf(pdf_path, 
              disciplina,
              relatorio_de_analise,
              conf_geral= None,

              e1_tabela = None,
              e1_ap=None,
              e1_tot= None,
              e1_rs= None,
              e1_rp= None,
              e1_pct= None,

              e2_tabela = None,
              e2_ap= None,
              e2_tot= None,
              e2_rp= None,
              e2_pct= None,

              e3_perguntas = None,
              e3_respostas = None
              ):

    # Pasta de fontes dentro do projeto
    font_dir = os.path.join(os.path.dirname(__file__), "fonts")

    # Registra todas as variações
    pdfmetrics.registerFont(TTFont("LiberationSans", os.path.join(font_dir, "LiberationSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("LiberationSans-Bold", os.path.join(font_dir, "LiberationSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("LiberationSans-Italic", os.path.join(font_dir, "LiberationSans-Italic.ttf")))
    pdfmetrics.registerFont(TTFont("LiberationSans-BoldItalic", os.path.join(font_dir, "LiberationSans-BoldItalic.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans", os.path.join(font_dir, "dejavu-sans.condensed.ttf")))

    # --- Fonte base ---
    fonte = 'LiberationSans'
    fonte_bold = "LiberationSans-Bold"

    # --- Estilos ---
    subtitle_style = ParagraphStyle(
        "Subtitle",
        fontName=fonte,   # <- aqui!
        fontSize=12,
        textColor=colors.HexColor("#2a6aa5"),
        spaceAfter=10,
    )

    badge_ok_style = ParagraphStyle(
        "BadgeOk",
        fontName=fonte,   # <- aqui também
        fontSize=10,
        textColor=colors.HexColor("#256029"),
        backColor=colors.HexColor("#c8e6c9"),
        alignment=1,  # centro
    )

    badge_no_style = ParagraphStyle(
        "BadgeNo",
        fontName=fonte,   # idem
        fontSize=10,
        textColor=colors.HexColor("#a94442"),
        backColor=colors.HexColor("#f8d7da"),
        alignment=1,  # centralizado
    )  
    
    note_style = ParagraphStyle(
        "Note",
        fontName=fonte,   # idem
        fontSize=9,
        textColor=colors.HexColor("#555555"),
    )

    # Função para converter hexadecimal para cores do ReportLab
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)/255
        g = int(hex_color[2:4], 16)/255
        b = int(hex_color[4:6], 16)/255
        return colors.Color(r, g, b)

    # número da primeira página
    def new_page():
        global page
        page +=1

        # --- Configurações do retângulo central ---
        largura = width - 50
        altura = height - 50
        x = (width - largura)/2
        y = (height - altura)/2
        raio_borda = 10

        # --- Finaliza a página ---
        c.showPage()

        # --- Fundo da página ---
        c.setFillColor(hex_to_rgb("#e6ecf3"))
        c.rect(0, 0, width, height, fill=1, stroke=0) # stroke = tamanho do traço (borda)

        # --- Retângulo branco central ---
        c.setFillColor(colors.white)
        c.roundRect(x, y, largura, altura, radius=raio_borda, stroke=0, fill=1)

        c.setFillColor(colors.black)
        # Cabeçalho
        c.setFont(fonte, 10)
        c.drawString(40, altura, ("Relatório da Avaliação de Completude - SEI " + dic_pr + " - BR " + dic_ro))
        
        # Rodapé
        c.setFont(fonte, 9)
        #c.drawString(50, 30, "Rodapé do documento")
        c.drawRightString(largura, y + 10, f"Página {page}")

    # Criar PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # --- Fundo da página ---
    c.setFillColor(hex_to_rgb("#e6ecf3"))
    c.rect(0, 0, width, height, fill=1, stroke=0) # stroke = tamanho do traço (borda)

    # --- Configurações do retângulo central ---
    largura = width - 50
    altura = height - 50
    x = (width - largura)/2
    y = (height - altura)/2
    raio_borda = 10

    # --- Retângulo branco central ---
    c.setFillColor(colors.white)
    c.roundRect(x, y, largura, altura, radius=raio_borda, stroke=0, fill=1)

    # --- Texto de exemplo ---
    c.setFillColor(colors.black)
    c.setFont(fonte, 30)
    yrel = y + altura - 50
    c.drawCentredString(width/2, yrel, disciplina)

    yrel-=30
    c.setFont(fonte, 26)
    c.drawCentredString(width/2, yrel, "Relatório da Avaliação de Completude")

    yrel-=30
    c.setFont(fonte, 11)
    c.drawCentredString(width/2, yrel, relatorio_de_analise)

    yrel-=15
    c.setFont(fonte, 11)
    c.drawCentredString(width/2, yrel, ("Data: " + datetime.now().strftime("%d/%m/%Y") + "  |  Hora: " + datetime.now().strftime("%H:%M")))
    yrel-=20

    c.setFillColor(colors.black)
    c.setFont(fonte, 9)
    c.drawRightString(largura, y + 10, f"Página {page}")

    # Dados da tabela
    dados_cabecalho = [
        ["Processo", dic_pr],
        ["Edital", dic_ed],
        ["Contrato", dic_co],
        ["Modalidade de Contratação", dic_mo],
        ["Rodovia", "BR " + dic_ro],
        ["Extensão", dic_ex],
        ["Lote", dic_lo],
        ["Tipo de projeto", dic_tp],
        ["Fase de projeto", dic_fa],
        ["Número da análise", dic_na],
        ["Número do último relatório", dic_nr],
        ["Analista", dic_an]
    ]

    c.setFont(fonte, 11)

    x_tabela = x+25
    y_tabela = yrel
    linha_altura = 20
    col_largura = [150, 150]  # largura de cada coluna

    # Desenha fundo cinza
    tabela_altura = linha_altura * len(dados_cabecalho)
    tabela_largura = sum(col_largura)
    c.setFillColor(hex_to_rgb("#f0f0f0"))
    c.rect(x_tabela, y_tabela - tabela_altura, tabela_largura, tabela_altura, fill=True, stroke=False)

    # Desenha bordas e conteúdo
    for i, linha in enumerate(dados_cabecalho):
        linha_y = y_tabela - i * linha_altura
        # desenha células
        col_x = x_tabela
        for j, item in enumerate(linha):
            c.setFillColor(colors.black)
            c.drawString(col_x + 2, linha_y - linha_altura + 5, str(item))  # +2 para dar padding
            c.setFillColor(hex_to_rgb("#eeeeeb"))
            c.rect(col_x, linha_y - linha_altura, col_largura[j], linha_altura,stroke=0, fill=False)
            col_x += col_largura[j]

    yrel= yrel - tabela_altura
        
    # --- Função para desenhar card ---
    def draw_card(c, x, y, w, h, title, etapa, subtitle="", title_size=22, subtitle_size=11):
        # Fundo
        c.setFillColor(colors.HexColor("#ebf5fb"))
        c.setStrokeColor(colors.HexColor("#aed6f1"))
        c.roundRect(x, y, w, h, fill=True, stroke=True, radius=5)

        # Título
        c.setFillColor(colors.HexColor("#0f4c81"))  # cor fixa usada no exemplo
        c.setFont("LiberationSans-Bold", title_size)
        c.drawCentredString(x + w/2, y + 6*h/10, title)

        # Etapa
        c.setFont(fonte, subtitle_size)
        c.drawCentredString(x + w/2, y + 3.5*h/10, etapa)

        # Subtítulo
        c.setFont(fonte, subtitle_size)
        c.drawCentredString(x + w/2, y + 1.5*h/10, subtitle)


    # --- Cards ---
    disciplinas_antecessoras= e1_tabela is not None
    cards = [
            (conf_geral, "Conformidade Geral", ""),
            (str(e1_ap + e1_rs)+" / " + str(e1_tot), "Etapa 01", "Disciplinas antecessoras") if e1_tabela is not None else ("- / -", "Etapa 01", "Disciplinas antecessoras"),
            (str(e2_ap)+" / " + str(e2_tot), "Etapa 02", "Relação de Documentos Gerais") if e2_tabela is not None else ("- / -", "Etapa 02", "Relação de Documentos Gerais"),
            ('- / -', "Etapa 03", "Conteúdo Relatório")
            ]

    # --- Desenha os cards em coluna ---
    w = 180
    h = 100
    espaco = 40

    draw_card(c, x + 25 + tabela_largura + 15, y_tabela - tabela_altura/2 - h/2, w, h, cards[0][0], cards[0][1])
    yrel-=(h+ 25)

    xrel = width/2 - 10 - w
    i = 0
    for titulo, etapa, subtitulo in cards[1:]:
        if i<2:
            draw_card(c, xrel, yrel, w, h, titulo, etapa, subtitulo)
        elif i == 2:
            xrel = width/2 - 10 - w
            yrel = yrel - h - 40
        draw_card(c, xrel, yrel, w, h, titulo, etapa, subtitulo)
        xrel += (w + espaco)
        i+=1


    # --------------------------------------------------------------
    
    if e1_tabela is not None:
        new_page()
        
        # Coordenada inicial
        y = height - 90

        #c.setFont('DejaVuSans', 16)
        # ---- Quadro Resumo ----
        p = Paragraph("Etapa 01 - Disciplinas antecessoras (Quadro Resumo)", subtitle_style)
        w, h = p.wrapOn(c, width - 100, y)
        p.drawOn(c, 50, y - h)
        y -= h + 10

        data_resumo = [
            ["Aprovado ✔", 
             "Com Ressalva ⚠", 
             "Reprovado ✖", 
             "% Aprovado", 
             "Status"],
            [str(e1_ap)+" / " + str(e1_tot), 
             str(e1_rs)+" / " + str(e1_tot), 
             str(e1_rp)+" / " + str(e1_tot), 
             str(e1_pct) + '%', 
             Paragraph("Aprovado", badge_ok_style) if e1_pct == 100 else Paragraph("Reprovado", badge_no_style)],
        ]

        table_resumo = Table(data_resumo, colWidths=[90, 110, 90, 80, 90])
        table_resumo.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),  # toda a tabela
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d9e1f2")),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        tw, th = table_resumo.wrapOn(c, width, y)
        table_resumo.drawOn(c, 50, y - th)
        y -= th + 20

        # ---- Quadro Detalhe ----
        p = Paragraph("Etapa 01 - Disciplinas antecessora (Quadro Detalhe)", subtitle_style)
        w, h = p.wrapOn(c, width - 100, y)
        p.drawOn(c, 50, y - h)
        y -= h + 10

        data_detalhe = [["Disciplina", "Aprovado", "Aprovado com Ressalva", "Reprovado", "Status"]]
        for i in range(len(e1_tabela)):
            lista_checks = list(e1_tabela.iloc[i]['STATUS'])
            for item in lista_checks:
                if item != "-":
                    lista_checks.append(item)
                    break
            data_detalhe.append(
                [e1_tabela.iloc[i]['DISCIPLINA']] + lista_checks
                )
        

        table_detalhe = Table(data_detalhe, colWidths=[140, 80, 120, 80, 70])
        table_detalhe.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),  # toda a tabela
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d9e1f2")),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        tw, th = table_detalhe.wrapOn(c, width, y)
        table_detalhe.drawOn(c, 50, y - th)
        y -= th + 20

        # ---- Nota ----
        '''
        p = Paragraph("Anotações: Arquivos Aprovados com Ressalva entram no status como Aprovado.", note_style)
        w, h = p.wrapOn(c, width - 100, y)
        p.drawOn(c, 50, y - h)
        y -= h + 20
        '''
    # -------------------------------------------------------
    if e2_tabela is not None:
        new_page()

        # Coordenada inicial
        y = height - 90

        # ---- Quadro Resumo ----
        p = Paragraph("Etapa 02 - Relação de Documentos Gerais (Quadro Resumo)", subtitle_style)
        w, h = p.wrapOn(c, width - 100, y)
        p.drawOn(c, 50, y - h)
        y -= h + 10
        
        data_resumo = [
            ["Aprovado ✔", 
            "Reprovado ✖", 
            "% Aprovado", 
            "Status"],
            [str(e2_ap)+" / " + str(e2_tot), 
            str(e2_rp)+" / " + str(e2_tot), 
            str(e2_pct) + '%', 
            Paragraph("Aprovado", badge_ok_style) if e2_pct == 100 else Paragraph("Reprovado", badge_no_style)],
        ]

        table_resumo = Table(data_resumo, colWidths=[90, 90, 80, 90])
        table_resumo.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),  # toda a tabela
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d9e1f2")),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        tw, th = table_resumo.wrapOn(c, width, y)
        table_resumo.drawOn(c, 50, y - th)
        y -= th + 20

        # ---- Quadro Detalhe ----
        p = Paragraph("Etapa 02 - Relação de Documentos Gerais (Quadro Detalhe)", subtitle_style)
        w, h = p.wrapOn(c, width - 100, y)
        p.drawOn(c, 50, y - h)
        y -= h + 10

        data_detalhe = [["Item", "Check"]]
        for i in range(len(e2_tabela)):
            data_detalhe.append(
                [e2_tabela.iloc[i]['VERIFICAÇÃO']] + [e2_tabela.iloc[i]['STATUS']]
                )

        table_detalhe = Table(data_detalhe, colWidths=[300, 70])
        table_detalhe.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),  # toda a tabela
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d9e1f2")),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        tw, th = table_detalhe.wrapOn(c, width, y)
        table_detalhe.drawOn(c, 50, y - th)
        y -= th + 20

        # ---- Nota ----
        '''
        p = Paragraph("Anotações: Arquivos Aprovados com Ressalva entram no status como Aprovado.", note_style)
        w, h = p.wrapOn(c, width - 100, y)
        p.drawOn(c, 50, y - h)
        y -= h + 20
        '''

    # --------------------------------------------------------
    new_page()

    # Coordenada inicial
    y = height - 90

    # ---- Quadro Resumo ----
    p = Paragraph("Etapa 03 - Conteúdo do Relatório (Quadro Resumo)", subtitle_style)
    w, h = p.wrapOn(c, width - 100, y)
    p.drawOn(c, 50, y - h)
    y -= h + 10

    import re
    from xml.sax.saxutils import escape

    def preparar_texto_reportlab(texto):
        # Padroniza tags de quebra de linha
        texto = re.sub(r'<br\s*>', '<br/>', texto, flags=re.I)

        # Protege temporariamente as tags <br/>
        marcador = "__BR_TEMP__"
        texto = texto.replace("<br/>", marcador)

        # Escapa caracteres HTML
        texto = escape(texto)

        # Restaura as quebras de linha
        texto = texto.replace(marcador, "<br/>")

        return texto

    styles = getSampleStyleSheet()
    style = styles["Normal"]

    # Dados da tabela
    dados = [['Pergunta', 'Resposta', 'Trecho que comprova']]
    for pergunta in range(len(e3_perguntas)):
        resp = re.findall(r"\d+\s*.\s*(.*?)(?=\n\d+\s*.|$)", e3_respostas[pergunta], re.S)

        if "sim" in resp[-1].lower():
            col2 = 'Sim'
        elif "não" in resp[-1].lower():
            col2 = 'Não'

        resp[-2] = resp[-2].replace("'''", "")
        resp[-2] = resp[-2].strip()
        resp[-2] = resp[-2].replace("\n\n\n", "\n\n")
        resp[-2] = resp[-2].strip()
        resp[-2] = resp[-2].strip()

        texto = preparar_texto_reportlab(resp[-2])

        dados.append([Paragraph(e3_perguntas[pergunta], style), col2, Paragraph(texto, style)])


    # Criar tabela
    tabela = LongTable(dados, colWidths=[150,50,300])

    # Estilo da tabela
    tabela.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9e1f2")),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))

    tw, th = tabela.wrapOn(c, width, y)
    tabela.drawOn(c, 50, y - th)
    y -= th + 20
    # ---- Nota ----
    
    p = Paragraph("Observações: A presente análise contou com o uso de sistemas de Inteligência Artificial como ferramenta de apoio, estando sujeita a limitações inerentes a essa tecnologia. As conclusões e decisões finais permanecem sob responsabilidade humana.", note_style)
    w, h = p.wrapOn(c, width - 100, y)
    p.drawOn(c, 50, y - h)
    y -= h + 20

    c.save()