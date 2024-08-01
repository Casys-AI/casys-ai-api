# src/application/services/similarity_processing_service.py

import logging
from typing import Dict, List, Any
import numpy as np
from src.domain.ports.embedding_adapter_protocol import EmbeddingAdapterProtocol
from src.domain.ports.neo4j_persistence_adapter_protocol import Neo4jPersistenceAdapterProtocol

logger = logging.getLogger("uvicorn.error")


class SimilarityProcessingService:
    def __init__(self, neo4j_adapter: Neo4jPersistenceAdapterProtocol, embedding_adapter: EmbeddingAdapterProtocol,
                 config: Dict[str, Any]):
        self.neo4j_adapter = neo4j_adapter
        self.embedding_adapter = embedding_adapter
        self.config = config

    def process_similarities(self, project_name: str) -> List[Dict[str, Any]]:
        logger.info(f"Processing similarities for project {project_name}")
        try:
            entities = self.neo4j_adapter.get_entities_for_similarity(project_name)
            logger.debug(f"Number of entities to process: {len(entities)}")

            similarities = self._calculate_similarities(entities)
            logger.info(f"Calculated {len(similarities)} similarity relationships")

            if similarities:
                self.neo4j_adapter.update_similarity_relationships(similarities)
            else:
                logger.warning("No similarities found to update")

            return similarities
        except Exception as e:
            logger.error(f"Error processing similarities: {str(e)}")
            return []


    def update_embeddings(self, project_name: str, diagram_type: str, entities: List[Dict[str, Any]]):

        embedding_dict = self.embedding_adapter.get_embeddings_dict(entities, diagram_type)
        self.neo4j_adapter.update_embeddings(project_name, diagram_type, embedding_dict)

    def _calculate_and_save_similarities(self, project_name: str, diagram_type: str):
        entities = self.neo4j_adapter.get_entities_for_similarity(project_name, diagram_type)
        similarities = self._calculate_similarities(entities)
        self.neo4j_adapter.create_similarity_relations(similarities)

    def _calculate_similarities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        similarities = []
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i + 1:]:
                if entity1['diagramType'] != entity2['diagramType']:
                    similarity = self._calculate_entity_similarity(entity1, entity2)
                    if similarity['combined_similarity'] > self.config["similarity"]["threshold"]:
                        similarities.append(similarity)
        return similarities

    def _calculate_entity_similarity(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> Dict[str, Any]:
        embedding_similarity = np.dot(entity1['embedding'], entity2['embedding']) / (
                np.linalg.norm(entity1['embedding']) * np.linalg.norm(entity2['embedding']))

        keyword_similarity = len(set(entity1['keywords']) & set(entity2['keywords'])) / len(
            set(entity1['keywords']) | set(entity2['keywords'])) if entity1['keywords'] and entity2['keywords'] else 0

        embedding_weight = self.config["similarity"]["embedding_weight"]
        keyword_weight = self.config["similarity"]["keyword_weight"]
        combined_similarity = (embedding_weight * embedding_similarity + keyword_weight * keyword_similarity) / (
                embedding_weight + keyword_weight)

        return {
            'id1': entity1['id'],
            'id2': entity2['id'],
            'combined_similarity': combined_similarity,
            'embedding_similarity': embedding_similarity,
            'keyword_similarity': keyword_similarity
        }