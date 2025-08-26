# src/models/product.py
from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    name: str
    price: Optional[str]
    company: Optional[str]
    description: Optional[str]
    link: Optional[str]
