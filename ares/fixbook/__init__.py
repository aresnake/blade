"""ARES FixBook — squelette minimal."""
import datetime
import json
import os
import pathlib

_FIX_DIR = pathlib.Path(__file__).parent
_BANK = _FIX_DIR / "bank_4_5.json"

def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_bank():
    if _BANK.exists():
        return json.loads(_BANK.read_text(encoding="utf-8"))
    return {"version": "4.5.x", "rules": []}

def suggest_fix(error: str) -> dict | None:
    bank = load_bank()
    for r in bank.get("rules", []):
        if any(k.lower() in error.lower() for k in r.get("keywords", [])):
            return r
    return None

def log_error(error: str, context: dict | None = None, out_dir: str | os.PathLike = "logs"):
    os.makedirs(out_dir, exist_ok=True)
    path = pathlib.Path(out_dir) / f"fixlog_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    payload = {"ts": _now(), "error": error, "context": context or {}, "suggested": suggest_fix(error)}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
