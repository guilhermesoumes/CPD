# -*- coding: utf-8 -*-
from funcs.rag_engine import answer_questions


def perguntas_IA(arquivo, lista_perguntas):
    """Compatibilidade com a API antiga dos scripts de verificacao."""
    return answer_questions(arquivo, lista_perguntas)
