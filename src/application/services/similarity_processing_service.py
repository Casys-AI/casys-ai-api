# src/application/services/similarity_processing_service.py
import numpy as np
from typing import List, Dict, Any


class SimilarityService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def calculate_similarities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        similarities = []
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i + 1:], start=i + 1):
                if entity1['diagramType'] != entity2['diagramType']:
                    similarity = self._calculate_entity_similarity(entity1, entity2)
                    if similarity['combined_similarity'] > self.config["similarity"]["threshold"]:
                        similarities.append(similarity)
        return similarities

    def _calculate_entity_similarity(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> Dict[str, Any]:
        embedding_similarity = self._cosine_similarity(entity1['embedding'], entity2['embedding'])

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

    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))