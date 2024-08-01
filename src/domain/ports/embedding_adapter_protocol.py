# src/domain/ports/embedding_adapter_protocol.py

from typing import List, Protocol


class EmbeddingAdapterProtocol(Protocol):
    """
    Protocol for embedding adapter classes.

    This protocol defines the methods required for embedding adapter classes. Embedding adapters are used to retrieve
    embeddings for texts, query strings, and entities.

    Methods:
    - get_embeddings(texts: List[str]) -> List[List[float]]: Returns the embeddings for a list of texts.
    - get_query_embedding(query: str) -> List[float]: Returns the embedding for a query string.
    - get_embeddings_dict(entities, diagram_type): Returns the embeddings dictionary for entities and diagram type.

    """
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        :param texts: A list of strings representing the texts for which the embeddings are to be obtained.
        :return: A list of lists of floats representing the embeddings of the given texts.
        """
        ...

    def get_query_embedding(self, query: str) -> List[float]:
        """

        get_query_embedding method returns the embedding of a given query.

        :param query: A string representing the query for which the embedding needs to be generated.
        :return: A list of floats representing the embedding of the given query.

        """
        ...

    def get_embeddings_dict(self, entities, diagram_type):
        """Returns a dictionary containing embeddings for entities.

        :param entities: List of entities for which embeddings need to be retrieved.
        :type entities: list[str]
        :param diagram_type: Type of diagram for which embeddings are needed.
        :type diagram_type: str
        :return: Dictionary containing embeddings for each entity.
        :rtype: dict[str, Any]
        """
        ...
