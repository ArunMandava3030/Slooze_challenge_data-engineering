#src\utils\storage.py
from pathlib import Path
from typing import Iterable, List
from src.parsers.models import Product

def ensure_dirs(paths: Iterable[str]):
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)

def dedupe_products(items: List[Product]) -> List[Product]:
    seen = set()
    out = []
    for it in items:
        key = (str(it.url or ""), (it.title or "").lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out
