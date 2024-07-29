# src/application/services/similarity_processing_service.py

import logging
from typing import Dict, List, Any
import numpy as np
from src.domain.ports.diagram_repository_port import DiagramRepositoryPort
from src.domain.ports.embedding_port import EmbeddingPort

logger = logging.getLogger(__name__)


class SimilarityProcessingService:
    """
    Constructs a new instance of the SimilarityProcessingService class.

    Args:
        repository (DiagramRepositoryPort): The repository to use for data access.
        embedding_service (EmbeddingPort): The service to use for calculating embeddings.
        config (Dict[str, Any]): The configuration settings.
    """
    def __init__(self, repository: DiagramRepositoryPort, embedding_service: EmbeddingPort, config: Dict[str, Any]):
        self.repository = repository
        self.embedding_service = embedding_service
        self.config = config

    def process_similarities(self, project_name: str, diagram_type: str, entities: List[Dict[str, Any]]):
        self.update_embeddings(project_name, diagram_type, entities)
        """
        Process similarities for a given diagram in a project.

        :param project_name: The name of the project.
        :param diagram_type: The type of diagram to process similarities for.
        :param entities: The list of entities to process similarities for.

        :return: None
        """
        logger.info(f"Processing similarities for diagram {diagram_type} in project {project_name}")

        self._update_embeddings(project_name, diagram_type, entities)
        self._calculate_and_save_similarities(project_name, diagram_type)

    def update_embeddings(self, project_name: str, diagram_type: str, entities: List[Dict[str, Any]]):
        """
        Met à jour les embeddings pour les entités données.

        Args:
            project_name (str): Nom du projet.
            diagram_type (str): Type de diagramme.
            entities (List[Dict[str, Any]]): Liste des entités.
        """
        embedding_dict = self.embedding_service.get_embeddings_dict(entities, diagram_type)
        self.repository.update_embeddings(project_name, diagram_type, embedding_dict)

    def _calculate_and_save_similarities(self, project_name: str, diagram_type: str):
        """
        :param project_name: The name of the project for which to calculate similarities.
        :param diagram_type: The type of diagram for which to calculate similarities.
        :return: None

        This method calculates similarities between entities in a given project and diagram type.

        It starts by retrieving the entities using the repository's `get_entities_for_similarity` method,
        which takes the project_name and diagram_type as parameters and returns a list of entities.

        Next, it calculates the similarities between the retrieved entities using the private method `_calculate_similarities`,
        which takes the list of entities as input and returns a dictionary of similarities.

        Finally, it saves the calculated similarities by calling the repository's `create_similarity_relations` method and passing in the similarities dictionary.

        Note: This method does not return any value.
        """
        entities = self.repository.get_entities_for_similarity(project_name, diagram_type)
        similarities = self._calculate_similarities(entities)
        self.repository.create_similarity_relations(similarities)

    def _calculate_similarities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        :param entities: A list of dictionaries representing entities with their attributes.
        :return: A list of dictionaries representing the similarities between entities.

        This method calculates the similarities between entities based on their diagram types. The method iterates over each entity and compares it with all the following entities. If the diagram types of the compared entities are different, the method calculates the similarity between them using the _calculate_entity_similarity method. If the combined similarity of the two entities is above the threshold value defined in the config, the similarity dictionary is added to the list of similarities.

        The method returns the list of calculated similarities.
        """
        similarities = []
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i + 1:]:
                if entity1['diagramType'] != entity2['diagramType']:
                    similarity = self._calculate_entity_similarity(entity1, entity2)
                    if similarity['combined_similarity'] > self.config["similarity"]["threshold"]:
                        similarities.append(similarity)
        return similarities

    def _calculate_entity_similarity(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> Dict[str, Any]:
        """
        :param entity1: A dictionary representing the first entity. Must contain the following keys:
            - 'embedding': A numpy array representing the embedding of the entity.
            - 'keywords': A list of keywords associated with the entity.
        :return: A dictionary containing the similarities between entity1 and entity2. The dictionary has the following keys:
            - 'id1': The id of entity1.
            - 'id2': The id of entity2.
            - 'combined_similarity': The combined similarity between entity1 and entity2.
            - 'embedding_similarity': The similarity based on the embeddings of entity1 and entity2.
            - 'keyword_similarity': The similarity based on the keywords of entity1 and entity2.

        """
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