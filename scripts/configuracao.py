"""Configuracao tecnica compartilhada pelos servicos locais de IA."""

from __future__ import annotations

URL_API_OPENAI = "http://127.0.0.1:1234/v1"
URL_API_MODELOS = "http://127.0.0.1:1234/api/v1/models"
CHAVE_API = "lm-studio"

MODELO_OCR = "glm-ocr"
MODELO_EMBEDDING = "text-embedding-qwen3-embedding-0.6b"
MODELO_CONVERSA = "google/gemma-3n-e4b"
MODELO_ART = "google/gemma-4-e2b"

MODELOS_CONHECIDOS = (
    MODELO_OCR,
    MODELO_EMBEDDING,
    MODELO_CONVERSA,
    MODELO_ART,
)

CONTEXTO_MODELO = 20_000
TIMEOUT_MODELO = 300
