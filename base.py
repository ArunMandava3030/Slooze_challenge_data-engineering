#src\collectors\base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseCollector(ABC):
    def __init__(self, config: Dict = None):
        self.config = config or {}

    @abstractmethod
    def collect(self, category: str, category_url: str, limit: int = 100, save_raw: bool = False) -> List[Dict[str, Any]]:
        """Return list of raw dicts ready for Pydantic validation."""
        raise NotImplementedError
