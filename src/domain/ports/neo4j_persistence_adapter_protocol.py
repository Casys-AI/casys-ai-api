from typing import Protocol, List, Dict, Any

class Neo4jPersistenceAdapterProtocol(Protocol):
    """
    Protocol for interacting with a Neo4j persistence adapter.

    This protocol defines the methods that should be implemented by a persistence adapter class for Neo4j.
    """
    
    def connect(self) -> None:
        """
        Establishes a connection to the Neo4j database.
        """
    
    def ensure_connection(self) -> None:
        """
        Ensures that a connection to the Neo4j database is established.
        """
    
    def is_connected(self) -> bool:
        """
        Check if the object is currently connected to the Neo4j database.

        :return: True if the object is connected, False otherwise.
        :rtype: bool
        """
    
    def ensure_vector_index(self) -> None:
        """
        Ensures that the vector index is created in the Neo4j database.
        """
    
    def batch_create_or_update_entities(self, project_name: str, diagram_type: str, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> None:
        """
        Creates or updates entities and relationships in the Neo4j database.

        :param project_name: The name of the project.
        :param diagram_type: The type of the diagram.
        :param entities: A list of dictionaries representing entities to be created or updated.
        :param relationships: A list of dictionaries representing relationships to be created or updated.
        """
    
    def create_or_update_project(self, project_name: str, project_type: str) -> None:
        """
        Creates or updates a project in the Neo4j database.

        :param project_name: The name of the project.
        :param project_type: The type of the project.
        """
    
    def create_or_update_diagram(self, project_name: str, diagram_type: str) -> None:
        """
        Creates or updates a diagram in the Neo4j database.

        :param project_name: The name of the project.
        :param diagram_type: The type of the diagram.
        """
    
    def update_similarity_relationships(self, similarities: List[Dict[str, Any]]) -> None:
        """
        Updates similarity relationships in the Neo4j database.

        :param similarities: A list of dictionaries representing similarity relationships.
        """
    
    def get_entities_for_similarity(self, project_name: str = None) -> List[Dict[str, Any]]:
        """
        Retrieves entities for similarity calculation from the Neo4j database.

        :param project_name: Optional. The name of the project to filter entities.
        :return: A list of dictionaries representing entities.
        """
    
    def rollback(self, project_name: str) -> None:
        """
        Rolls back changes for a specific project in the Neo4j database.

        :param project_name: The name of the project to rollback.
        """
    
    def close(self) -> None:
        """
        Closes the connection to the Neo4j database.
        """
    
    def update_embeddings(self, project_name, diagram_type, embeddings):
        pass
    