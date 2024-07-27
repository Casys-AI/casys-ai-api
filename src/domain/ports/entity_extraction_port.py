# src/domain/ports/entity_extraction_port.py
class EntityExtractionPort:
    def extract_entities_and_relationships(self, diagram_content):
        raise NotImplementedError("This method should be overridden")
