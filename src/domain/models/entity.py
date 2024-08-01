from typing import List

from dataclasses import dataclass


@dataclass
class Entity:
    def __init__(self, name: str, entity_type: str, description: str, keywords: List[str]):
        self.name = name
        self.type = entity_type
        self.description = description
        self.keywords = keywords
