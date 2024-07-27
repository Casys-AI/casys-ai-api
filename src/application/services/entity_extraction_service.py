# src/application/services/entity_extraction_service.py
from src.domain.ports.entity_extraction_port import EntityExtractionPort
import logging
logger = logging.getLogger(__name__)
class EntityExtractionService:
    def __init__(self, entity_extraction_port: EntityExtractionPort):
        self.entity_extraction_port = entity_extraction_port

    # Dans entity_extraction_service.py
    def extract_entities_and_relationships(self, diagram_content):
        if not diagram_content:
            logger.warning("Le contenu du diagramme est vide")
            return {"entities": [], "relationships": []}

        result = self.entity_extraction_port.extract_entities_and_relationships(diagram_content)

        if not result.get("entities") and not result.get("relationships"):
            logger.warning("Aucune entité ou relation n'a été extraite")

        return result