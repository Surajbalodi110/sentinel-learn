"""Local progress store: survives page reloads (nav links do full reloads)."""

import json
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "progress.json")

def _norm(path: str) -> str:
    return os.path.normpath(path if os.path.isabs(path) else os.path.join(os.getcwd(), path))

def load() -> dict:
    try:
        with open(_norm(PATH), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def save(state: dict) -> None:
    try:
        p = _norm(PATH)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f)
        os.replace(tmp, p)
    except Exception:
        pass
