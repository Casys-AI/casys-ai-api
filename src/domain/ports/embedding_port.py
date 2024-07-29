# src/domain/ports/embedding_port.py

from abc import ABC, abstractmethod
from typing import List

class EmbeddingPort(ABC):
    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Génère des embeddings pour une liste de textes.

        Args:
            texts (List[str]): Liste de textes à encoder.

        Returns:
            List[List[float]]: Liste des embeddings correspondants.
                Chaque embedding est une liste de nombres flottants.
        """
        pass

    @abstractmethod
    def get_query_embedding(self, query: str) -> List[float]:
        """
        Génère un embedding pour une seule requête.

        Cette méthode est utile pour les cas où vous avez besoin d'un
        embedding pour une seule chaîne de texte, comme dans le cas
        d'une requête de recherche.

        Args:
            query (str): Le texte de la requête à encoder.

        Returns:
            List[float]: L'embedding de la requête sous forme de liste de nombres flottants.
        """
        pass