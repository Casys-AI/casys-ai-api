from dataclasses import dataclass


@dataclass
class Relationship:
    def __init__(self, source: str, target: str, relationship_type: str):
        self.source = source
        self.target = target
        self.type = relationship_type
