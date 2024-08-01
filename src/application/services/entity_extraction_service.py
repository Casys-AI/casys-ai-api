# src/application/services/entity_extraction_service.py
from src.domain.ports.entity_extraction_adapter_protocol import EntityExtractionAdapterProtocol
import logging

logger = logging.getLogger("uvicorn.error")


class EntityExtractionService:
    def __init__(self, entity_extraction_adapter: EntityExtractionAdapterProtocol):
        self.entity_extraction_adapter = entity_extraction_adapter

    # Dans entity_extraction_service.py
    def extract_entities_and_relationships(self, diagram_content):
        if not diagram_content:
            logger.warning("Le contenu du diagramme est vide")
            return {"entities": [], "relationships": []}

        result = self.entity_extraction_adapter.extract_entities_and_relationships(diagram_content)

        if not result.get("entities") and not result.get("relationships"):
            logger.warning("Aucune entité ou relation n'a été extraite")

        return result
