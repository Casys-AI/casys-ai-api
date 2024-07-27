# src/domain/ports/diagram_repository_port.py
from src.domain.models.diagram import Diagram

class DiagramRepositoryPort:
    def save(self, diagram: Diagram):
        raise NotImplementedError("This method should be overridden")
