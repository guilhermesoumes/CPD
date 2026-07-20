"""Testes unitarios dos contratos puros compartilhados pelos scripts."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from scripts.executor_verificacoes import _resposta_art
from scripts.funcoes_comuns import padronizar_lote, proximo_nome_relatorio
from templates.relatorio_pdf import contagem_pontuacao


class FuncoesComunsTests(unittest.TestCase):
    def test_padronizar_lote_numerico_e_alfanumerico(self) -> None:
        self.assertEqual(padronizar_lote("1"), "01")
        self.assertEqual(padronizar_lote("2b"), "02B")
        self.assertEqual(padronizar_lote("especial"), "especial")

    def test_proximo_nome_relatorio_incrementa_maior_versao(self) -> None:
        arquivos = []
        for nome in (
            "RAC-001-2026_BR-040-DF_PGMT_LT-01.pdf",
            "RAC-003-2026_BR-040-DF_PGMT_LT-01.pdf",
        ):
            arquivo = MagicMock()
            arquivo.name = nome
            arquivo.is_file.return_value = True
            arquivos.append(arquivo)

        diretorio = MagicMock()
        diretorio.iterdir.return_value = arquivos
        with patch("scripts.funcoes_comuns.Path", return_value=diretorio):
            nome = proximo_nome_relatorio(
                "resultados", "2026", "040-DF", "PGMT", "01"
            )

            self.assertEqual(nome, "RAC-004-2026_BR-040-DF_PGMT_LT-01")


class RespostasTests(unittest.TestCase):
    def test_resposta_art_sem_paginas(self) -> None:
        self.assertEqual(_resposta_art([]), "1. Nao\n2. -\n3. Nao")

    def test_resposta_art_com_paginas(self) -> None:
        resposta = _resposta_art([2, 5])
        self.assertIn("na pagina: 2", resposta)
        self.assertIn("na pagina: 5", resposta)
        self.assertTrue(resposta.endswith("3. Sim"))

    def test_pontuacao(self) -> None:
        respostas = [
            "1. Sim\n2. evidencia\n3. Sim",
            "1. Nao\n2. -\n3. Nao",
        ]
        self.assertEqual(contagem_pontuacao(respostas), 50.0)


if __name__ == "__main__":
    unittest.main()
