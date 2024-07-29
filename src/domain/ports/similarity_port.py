# src/domain/ports/diagram_repository_port.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from src.domain.models.diagram import Diagram


class SimilarityPort(ABC):

    @abstractmethod
    def save(self, diagram: Diagram):
        """
        Sauvegarde un diagramme entier.
        """
        pass



    @abstractmethod
    def update_embeddings(self, project_name: str, diagram_type: str, embeddings: Dict[str, List[float]]):
        """
        Met à jour les embeddings des entités d'un diagramme spécifique.
        """
        pass


    @abstractmethod
    def get_entities_for_similarity(self, project_name: str, diagram_type: str = None) -> List[Dict[str, Any]]:
        """
        Récupère les entités avec leurs embeddings et mots-clés pour le calcul de similarité.
        """
        pass


    @abstractmethod
    def close(self):
        """
        Ferme la connexion à la base de données si nécessaire.
        """
        pass