import logging
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings

from src.domain.ports.embedding_adapter_protocol import EmbeddingAdapterProtocol

logger = logging.getLogger("uvicorn.error")


class OpenAIEmbeddingAdapter(EmbeddingAdapterProtocol):
    def __init__(self, embeddings_model: OpenAIEmbeddings):
        self.embeddings_model = embeddings_model
    
    @classmethod
    def create(cls, api_key: str):
        embeddings_model = OpenAIEmbeddings(openai_api_key=api_key)
        return cls(embeddings_model)
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            embeddings = self.embeddings_model.embed_documents(texts)
            if not all(isinstance(emb, list) and all(isinstance(x, float) for x in emb) for emb in embeddings):
                raise ValueError("Invalid embedding format")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}", exc_info=True)
            return []
    
    def get_query_embedding(self, query: str) -> List[float]:
        try:
            return self.embeddings_model.embed_query(query)
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}", exc_info=True)
            return []
    
    def get_embeddings_dict(self, entities: List[Dict[str, Any]], diagram_type: str) -> Dict[str, List[float]]:
        embeddings_dict = {}
        for index, entity in enumerate(entities):
            if 'description' in entity:
                entity_id = entity.get('id', f"{diagram_type}_{index}")
                try:
                    embedding = self.get_embeddings([entity['description']])[0]
                    embeddings_dict[entity_id] = embedding
                    logger.debug(f"Generated embedding for entity {entity_id}: {embedding[:5]}...")
                except Exception as e:
                    logger.error(f"Error generating embedding for entity {entity_id}: {str(e)}", exc_info=True)
        
        logger.info(f"Successfully generated embeddings for {len(embeddings_dict)} entities")
        return embeddings_dict