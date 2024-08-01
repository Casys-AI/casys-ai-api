from typing import Protocol, List, Dict, Any


class Neo4jPersistenceAdapterProtocol(Protocol):
    """
    Protocol for interacting with a Neo4j persistence adapter.

    This protocol defines the methods that should be implemented by a persistence adapter class for Neo4j.

    """
    def save(self, project_name: str, diagram_type: str, entities: List[Dict[str, Any]],
             relationships: List[Dict[str, Any]]) -> None:
        """

        **save**

        Saves the project with the given project name, diagram type, and entities/relationships.

        :param project_name: The name of the project to save.
        :type project_name: str

        :param diagram_type: The type of diagram to save.
        :type diagram_type: str

        :param entities: The list of entities to save. Each entity is represented as a dictionary.
        :type entities: List[Dict[str, Any]]

        :param relationships: The list of relationships to save. Each relationship is represented as a dictionary.
        :type relationships: List[Dict[str, Any]]

        :return: None        :rtype:

        """

    def ensure_vector_index(self) -> None:
        """
        Ensures that the vector index is valid.

        :return: None
        """

    def get_entities_for_similarity(self, project_name, diagram_type):
        pass

    def create_similarity_relations(self, similarities):
        pass

    def batch_create_or_update_entities(self, entities: List[Dict[str, Any]], project_name: str,
                                        project_label: str) -> None:
        """
        Batch create or update entities in the specified project.

        :param entities: A list of dictionaries representing the entities to be created or updated.
                         Each dictionary should contain the necessary attributes for the entity.
        :type entities: List[Dict[str, Any]]

        :param project_name: The name of the project where the entities will be created or updated.
        :type project_name: str

        :param project_label: A label that uniquely identifies the project where the entities will be created or updated.
        :type project_label: str

        :return: None
        """

    def batch_create_relationships(self, relationships: List[Dict[str, Any]], project_name: str) -> None:
        """
        Create multiple relationships in batch for a given project.

        :param relationships: A list of dictionaries representing the relationships to create.
            Each dictionary should contain the necessary information to create a relationship.
        :param project_name: The name of the project in which to create the relationships.
        :return: None
        """

    def update_embeddings(self, project_name: str, diagram_type: str, embeddings: dict[str, list[float]]) -> None:
        """
        Update the embeddings for a specific project and diagram type.

        :param project_name: The name of the project.
        :param diagram_type: The type of the diagram.
        :param embeddings: A dictionary mapping entity names to their embeddings represented as a list of floats.
        :return: None
        """

    def calculate_similarities_with_existing(self, new_entity_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Calculates similarities between new entity IDs and existing entities.

        :param new_entity_ids: List of new entity IDs.
        :return: List of dictionaries containing similarities between new entity IDs and existing entities.
        :rtype: List[Dict[str, Any]]
        """

    def update_similarity_relationships(self, similarities: List[Dict[str, Any]]) -> None:
        """
        Update the similarity relationships.

        :param similarities: A list of dictionaries representing the similarity relationships. Each dictionary should have the following keys:
            - 'id': The ID of the similarity relationship.
            - 'similarity': The similarity score between two entities.
            - 'entity1_id': The ID of the first entity.
            - 'entity2_id': The ID of the second entity.
        :return: None

        """

    def rollback(self, project_name: str) -> None:
        """
        :param project_name: The name of the project to rollback.
        :return: None.

        """

    def is_connected(self) -> bool:
        """
        Check if the object is currently connected.

        :return: True if the object is connected, False otherwise.
        :rtype: bool
        """

    def close(self) -> None:
        """
        Closes the connection.

        :return:
            None
        """
