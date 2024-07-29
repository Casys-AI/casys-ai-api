# src/application/services/similarity_processing_service.py

import logging
from typing import Dict, List, Any

import numpy as np

from src.domain.ports.diagram_repository_port import DiagramRepositoryPort
from src.domain.ports.embedding_port import EmbeddingPort

logger = logging.getLogger(__name__)


class SimilarityProcessingService:
    def __init__(self, repository: DiagramRepositoryPort, embedding_service: EmbeddingPort, config: Dict[str, Any]):
        self.repository = repository
        self.embedding_service = embedding_service
        self.config = config

    def process_diagram(self, project_name: str, diagram_type: str, entities: List[Dict[str, Any]],
                        relationships: List[Dict[str, Any]]):
        logger.info(f"Processing diagram {diagram_type} for project {project_name}")

        prepared_entities = [self._prepare_entity(entity, diagram_type) for entity in entities]
        prepared_relationships = [self._prepare_relationship(rel, diagram_type) for rel in relationships]

        self.repository.save(project_name, diagram_type, prepared_entities, prepared_relationships)

        self._update_embeddings(project_name, diagram_type, prepared_entities)
        self._process_similarities(project_name, diagram_type)

    def _prepare_entity(self, entity: Dict[str, Any], diagram_type: str) -> Dict[str, Any]:
        entity['id'] = f"{diagram_type}_{entity['name']}"
        return entity

    def _prepare_relationship(self, relationship: Dict[str, Any], diagram_type: str) -> Dict[str, Any]:
        relationship['source_id'] = f"{diagram_type}_{relationship['source']}"
        relationship['target_id'] = f"{diagram_type}_{relationship['target']}"
        return relationship

    def _update_embeddings(self, project_name: str, diagram_type: str, entities: List[Dict[str, Any]]):
        descriptions = [entity['description'] for entity in entities if 'description' in entity]
        embeddings = self.embedding_service.get_embeddings(descriptions)

        embedding_dict = {
            entity['id']: embedding
            for entity, embedding in zip(entities, embeddings)
            if 'description' in entity
        }

        self.repository.update_embeddings(project_name, diagram_type, embedding_dict)

    def _process_similarities(self, project_name: str, diagram_type: str = None):
        entities = self.repository.get_entities_for_similarity(project_name, diagram_type)
        similarities = self._calculate_similarities(entities)
        self.repository.create_similarity_relations(similarities)

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
