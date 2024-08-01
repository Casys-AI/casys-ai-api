# src/domain/ports/diagram_repository_adapter_protocol.py

from typing import Protocol

from src.domain.models.diagram import Diagram


class DiagramRepositoryProtocol(Protocol):

    def save(self, diagram: Diagram):
        """
        Sauvegarde un diagramme entier.
        """
        pass
