# src/domain/ports/entity_extraction_adapter_protocol.py

from typing import Dict, Any, Protocol


class EntityExtractionAdapterProtocol(Protocol):
    """
    EntityExtractionAdapterProtocol

    Protocol that defines the interface for extracting entities and relationships from a diagram content.

    Methods:
        extract_entities_and_relationships(diagram_content: str) -> Dict[str, Any]
            Extracts entities and relationships from the given diagram content.

    Parameters:
        - diagram_content (str): The content of the diagram to be processed.

    Returns:
        - Dict[str, Any]: A dictionary containing the extracted entities and relationships.
    """
    def extract_entities_and_relationships(self, diagram_content: str) -> Dict[str, Any]:
        """
        Extracts entities and relationships from diagram content.

        :param diagram_content: The content of the diagram.
        :return: A dictionary containing the extracted entities and relationships.
        """
        ...
