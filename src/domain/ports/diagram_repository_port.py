# src/domain/ports/diagram_repository_port.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from src.domain.models.diagram import Diagram

class DiagramRepositoryPort(ABC):
    @abstractmethod
    def save(self, diagram: Diagram):
        """
        Sauvegarde un diagramme entier.
        """
        pass
