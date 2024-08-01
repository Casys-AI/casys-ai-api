from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Diagram:
    name: str
    data: Dict[str, Any]
