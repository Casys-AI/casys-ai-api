# src/application/services/similarity_processing_service.py
import numpy as np
from typing import List, Dict, Any, Set
import logging

logger = logging.getLogger("uvicorn.error")


class SimilarityService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def calculate_similarities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"Calculating similarities for {len(entities)} entities")
        similarities = []
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i + 1:], start=i + 1):
                # Comparer les entités de diagrammes différents, peu importe le type ou le projet
                if entity1['id'] != entity2['id']:  # Assurez-vous que l'entité n'est pas comparée à elle-même
                    similarity = self._calculate_entity_similarity(entity1, entity2)
                    logger.debug(f"Similarity between {entity1['id']} and {entity2['id']}: {similarity['combined_similarity']}")
                    if similarity['combined_similarity'] > self.config["similarity"]["threshold"]:
                        similarities.append(similarity)
                    else:
                        logger.debug(f"Similarity below threshold: {similarity['combined_similarity']} < {self.config['similarity']['threshold']}")

        logger.info(f"Found {len(similarities)} similarities above threshold")
        return similarities

    def _calculate_entity_similarity(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> Dict[str, Any]:
        embedding_similarity = self._cosine_similarity(entity1['embedding'], entity2['embedding'])
        jaccard_similarity = self._contextual_jaccard_similarity(entity1, entity2)

        embedding_weight = self.config["similarity"]["embedding_weight"]
        keyword_weight = self.config["similarity"]["keyword_weight"]
        combined_similarity = (embedding_weight * embedding_similarity + keyword_weight * jaccard_similarity) / (
                embedding_weight + keyword_weight)

        return {
            'id1': entity1['id'],
            'id2': entity2['id'],
            'project_name1': entity1['project_name'],
            'project_name2': entity2['project_name'],
            'diagram_type1': entity1['diagram_type'],
            'diagram_type2': entity2['diagram_type'],
            'combined_similarity': combined_similarity,
            'embedding_similarity': embedding_similarity,
            'jaccard_similarity': jaccard_similarity
        }

    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    @staticmethod
    def _contextual_jaccard_similarity(entity1: Dict[str, Any], entity2: Dict[str, Any]) -> float:
        set1 = SimilarityService._create_contextual_set(entity1)
        set2 = SimilarityService._create_contextual_set(entity2)

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0.0

    @staticmethod
    def _create_contextual_set(entity: Dict[str, Any]) -> Set[str]:
        contextual_set = set()
        contextual_set.add(f"project:{entity['project_name']}")
        contextual_set.add(f"diagram:{entity['diagram_type']}")
        contextual_set.add(f"entity:{entity['name']}")
        contextual_set.update(f"keyword:{kw}" for kw in entity['keywords'])
        return contextual_set
