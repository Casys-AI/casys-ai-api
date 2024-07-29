# src/domain/ports/rag_port.py
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

class RAGPort(ABC):
    @abstractmethod
    def hybrid_search_with_fallback(self, query: str, semantic_top_k: int = 5, graph_depth: int = 2) -> List[Tuple[str, str]]:
        """
        Effectue une recherche hybride avec repli sur une recherche par mots-clés.

        Args:
            query (str): La requête de recherche.
            semantic_top_k (int): Le nombre de résultats sémantiques les plus pertinents à retourner.
            graph_depth (int): La profondeur de la recherche dans le graphe.

        Returns:
            List[Tuple[str, str]]: Une liste de tuples (nom, description) des entités trouvées.
        """
        pass

    @abstractmethod
    def rag_pipeline(self, content: str, prompt_template: str) -> Tuple[Optional[str], bool]:
        """
        Exécute le pipeline RAG complet.

        Args:
            content (str): Le contenu à analyser.
            prompt_template (str): Le template de prompt à utiliser.

        Returns:
            Tuple[Optional[str], bool]: Le résultat généré et un booléen indiquant le succès de l'opération.
        """
        pass