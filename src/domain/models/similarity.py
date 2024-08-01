from src.domain.models.entity import Entity

from dataclasses import dataclass


@dataclass
class Similarity:
    def __init__(self, entity1: Entity, entity2: Entity, score: float):
        self.entity1 = entity1
        self.entity2 = entity2
        self.score = score
