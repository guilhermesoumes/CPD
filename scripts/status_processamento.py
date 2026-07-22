"""Canal leve de eventos para exibir o andamento do processamento na interface."""

from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from typing import Any

CallbackStatus = Callable[[dict[str, Any]], None]
_callback: CallbackStatus | None = None
_lock = Lock()


def definir_callback(callback: CallbackStatus | None) -> None:
    """Define o consumidor dos eventos da execução atual."""
    global _callback
    with _lock:
        _callback = callback


def informar(etapa: str, mensagem: str, **detalhes: Any) -> None:
    """Publica um evento; falhas de exibição nunca interrompem o processamento."""
    with _lock:
        callback = _callback
    if callback is None:
        return
    try:
        callback({"etapa": etapa, "mensagem": mensagem, **detalhes})
    except Exception:
        pass
