# src/adapters/web/openai_embedding_adapter.py

import logging
from typing import List,Dict, Any
from langchain_openai import OpenAIEmbeddings as openai_embeddings


logger = logging.getLogger("uvicorn.error")


class OpenAIEmbeddingAdapter:
    def __init__(self, api_key: str):
        self.embeddings_model = openai_embeddings(openai_api_key=api_key)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            embeddings = self.embeddings_model.embed_documents(texts)
            # Vérification du format
            if not all(isinstance(emb, list) and all(isinstance(x, float) for x in emb) for emb in embeddings):
                raise ValueError("Invalid embedding format")
            return embeddings
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
        embeddings_dict = {}
        for index, entity in enumerate(entities):
            if 'description' in entity:
                # Générer un ID temporaire si non présent
                entity_id = entity.get('id', f"{diagram_type}_{index}")
                embedding = self.get_embeddings([entity['description']])[0]
                embeddings_dict[entity_id] = embedding
                logger.debug(f"Generated embedding for entity {entity_id}: {embedding[:5]}...")

        logger.info(f"Successfully generated embeddings for {len(embeddings_dict)} entities")
        return embeddings_dict