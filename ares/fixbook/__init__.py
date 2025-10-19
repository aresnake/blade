from __future__ import annotations

import datetime
import json
import os
import pathlib

__all__ = ["log_error", "suggest_fix"]


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def suggest_fix(error: str) -> str:
    # heuristique minuscule pour proposer un début de piste
    if "ModuleNotFoundError" in error:
        return "Vérifie PYTHONPATH/installation de l'addon, puis relance."
    if "AttributeError" in error:
        return "API Blender différente ? Ajoute un guard ou adapte l'appel."
    return "Voir le log ci-dessous et reproduire en -b pour un patch ciblé."


def log_error(error: str, context: dict | None = None, out_dir: str | os.PathLike = "logs"):
    os.makedirs(out_dir, exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = pathlib.Path(out_dir) / f"fixlog_{ts}.json"

    payload = {
        "ts": _now(),
        "error": error,
        "context": context or {},
        "suggested": suggest_fix(error),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
