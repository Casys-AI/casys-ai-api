# src/adapters/web/openai_embedding_adapter.py

import logging
from typing import List,Dict, Any
from langchain_openai import OpenAIEmbeddings
from src.domain.ports.embedding_port import EmbeddingPort

logger = logging.getLogger(__name__)


class OpenAIEmbeddingAdapter(EmbeddingPort):
    def __init__(self, api_key: str):
        self.embeddings_model = OpenAIEmbeddings(openai_api_key=api_key)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            return self.embeddings_model.embed_documents(texts)
        except Exception as e:
            logger.error(f"Erreur lors de la génération des embeddings : {str(e)}")
            return []

    def get_query_embedding(self, query: str) -> List[float]:
        try:
            return self.embeddings_model.embed_query(query)
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'embedding de requête : {str(e)}")
            return []

    def get_embeddings_dict(self, entities: List[Dict[str, Any]], diagram_type: str) -> Dict[str, List[float]]:
        """
        Génère un dictionnaire d'embeddings pour les entités données.

        Args:
            entities (List[Dict[str, Any]]): Liste des entités.
            diagram_type (str): Type de diagramme.

        Returns:
            Dict[str, List[float]]: Dictionnaire des embeddings.
        """
        descriptions = [entity['description'] for entity in entities if 'description' in entity]
        embeddings = self.get_embeddings(descriptions)

        return {
            f"{diagram_type}_{entity['name']}": embedding
            for entity, embedding in zip(entities, embeddings)
            if 'description' in entity
        }