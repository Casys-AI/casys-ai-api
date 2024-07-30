import logging
import json
from typing import Dict, Any
from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter

logger = logging.getLogger(__name__)


class Neo4jProcessingService:
    @staticmethod
    async def process_neo4j_data(neo4j_adapter: Neo4jPersistenceAdapter, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            logger.info(f"Starting Neo4j data processing for project: {project_name}, diagram: {diagram_type}")

            neo4j_adapter.ensure_vector_index()

            file_path = f"diagrams/{project_name}/{diagram_type}_entities.json"
            data = Neo4jProcessingService._process_json_file(file_path)

            neo4j_adapter.batch_create_or_update_entities(data['entities'], project_name, project_name.upper())
            neo4j_adapter.batch_create_relationships(data['relationships'], project_name)

            neo4j_adapter.update_embeddings(project_name, diagram_type)

            new_entity_ids = [f"{diagram_type}_{entity['name']}" for entity in data['entities']]
            similarities = neo4j_adapter.calculate_similarities_with_existing(new_entity_ids)

            neo4j_adapter.update_similarity_relationships(similarities)

            logger.info(f"Neo4j data processing and similarity calculation completed for project: {project_name}, diagram: {diagram_type}")
            return {"status": "completed", "message": f"Neo4j data processing and similarity calculation completed for {project_name}, {diagram_type}"}
        except Exception as e:
            logger.exception(f"Error during Neo4j data processing: {str(e)}")
            neo4j_adapter.rollback(project_name)
            return {"status": "error", "message": f"Error during Neo4j data processing for {project_name}, {diagram_type}: {str(e)}"}

    @staticmethod
    def _process_json_file(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"JSON file processed successfully: {file_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from file {file_path}: {str(e)}")
            raise
        except IOError as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing JSON file {file_path}: {str(e)}")
            raise