# src/domain/ports/entity_extraction_port.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class EntityExtractionPort(ABC):
    @abstractmethod
    def extract_entities_and_relationships(self, diagram_content: str) -> Dict[str, Any]:
        """
        Extrait les entités et les relations à partir du contenu du diagramme.

        Args:
            diagram_content (str): Le contenu du diagramme à analyser.

        Returns:
            Dict[str, Any]: Un dictionnaire contenant les entités et les relations extraites.
        """
        pass