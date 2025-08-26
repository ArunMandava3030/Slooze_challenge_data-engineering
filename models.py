#src\parsers\models.py
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, field_validator
from pathlib import Path
import pandas as pd

class Product(BaseModel):
    marketplace: str
    category: str
    title: str
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: Optional[str] = None
    unit: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_location: Optional[str] = None
    url: Optional[str] = None
    source_html_snippet: Optional[str] = None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, v):
        if not v:
            return v
        v = v.upper().strip().replace("RS.", "INR").replace("RS", "INR")
        if v in {"₹", "INR", "USD"}:
            return v
        return v

    @field_validator("title")
    @classmethod
    def clean_title(cls, v):
        return " ".join(v.split()) if v else v

def to_jsonl(items: List[Product], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(it.model_dump_json() + "\n")

def to_csv(items: List[Product], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([it.model_dump() for it in items])
    df.to_csv(path, index=False)
