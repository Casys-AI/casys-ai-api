# src/application/services/neo4j_processing_service.py

import logging
import json
from typing import Dict, Any, List

from src.application.services.project_management_service import ProjectManagementService
from src.application.services.similarity_processing_service import SimilarityService
from src.domain.ports.embedding_adapter_protocol import EmbeddingAdapterProtocol
from src.domain.ports.neo4j_persistence_adapter_protocol import Neo4jPersistenceAdapterProtocol
from src.domain.ports.async_task_port import AsyncTaskPort

logger = logging.getLogger("uvicorn.error")


def _process_json_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"JSON file processed successfully: {file_path}")
        logger.debug(f"JSON content: {data}")
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


class Neo4jProcessingService:
    def __init__(self, project_manager: ProjectManagementService,
                 embedding_adapter: EmbeddingAdapterProtocol,
                 neo4j_adapter: Neo4jPersistenceAdapterProtocol,
                 similarity_service: SimilarityService,
                 async_task_adapter: AsyncTaskPort):
        self.project_manager = project_manager
        self.embedding_adapter = embedding_adapter
        self.neo4j_adapter = neo4j_adapter
        self.similarity_service = similarity_service
        self.async_task_adapter = async_task_adapter
    
    @staticmethod
    def _add_temp_ids_to_entities(entities: List[Dict[str, Any]], diagram_type: str) -> List[Dict[str, Any]]:
        return [
            {**entity, 'id': entity.get('id', f"{diagram_type}_{index}")}
            for index, entity in enumerate(entities)
        ]
    
    def _process_neo4j_data(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            logger.info(f"Starting Neo4j data processing for project: {project_name}, diagram: {diagram_type}")
            
            project = self.project_manager.find_project(project_name)
            entities_path = self.project_manager.get_project_entities_path(project_name, diagram_type)
            
            data = _process_json_file(entities_path)
            entities = self._add_temp_ids_to_entities(data['entities'], diagram_type)
            relationships = data.get('relationships', [])
            
            embeddings = self.embedding_adapter.get_embeddings_dict(entities, diagram_type)
            
            all_entities = self.neo4j_adapter.get_entities_for_similarity(project_name)
            similarities = self.similarity_service.calculate_similarities(all_entities)
            
            self.neo4j_adapter.create_or_update_project(project_name, project['type'])
            self.neo4j_adapter.create_or_update_diagram(project_name, diagram_type)
            self.neo4j_adapter.create_or_update_entities_and_keywords(project_name, diagram_type, entities)
            self.neo4j_adapter.update_embeddings(project_name, diagram_type, embeddings)
            self.neo4j_adapter.create_relationships(project_name, diagram_type, relationships)
            self.neo4j_adapter.update_similarity_relationships(similarities)
            
            logger.info(f"Neo4j data processing completed for project: {project_name}, diagram: {diagram_type}")
            return {"status": "completed",
                    "message": f"Neo4j data processing completed for {project_name}, {diagram_type}"}
        except Exception as e:
            logger.error(f"Error during Neo4j data processing: {str(e)}")
            return {"status": "failed",
                    "message": f"Neo4j data processing failed for {project_name}, {diagram_type}. Error: {str(e)}"}
    
    def _process_entire_project(self, project_name: str) -> Dict[str, Any]:
        try:
            logger.info(f"Starting Neo4j data processing for entire project: {project_name}")
            
            self.neo4j_adapter.ensure_vector_index()
            
            project = self.project_manager.find_project(project_name)
            diagram_types = self.project_manager.get_diagram_types()
            
            results = []
            for diagram_type in diagram_types:
                logger.info(f"Processing diagram type: {diagram_type}")
                result = self._process_neo4j_data(project_name, diagram_type)
                results.append(result)
                if result['status'] == 'failed':
                    return {"status": "error", "message": f"Processing failed for diagram type: {diagram_type}",
                            "results": results}
            
            logger.info(f"Neo4j data processing completed for entire project: {project_name}")
            return {"status": "completed",
                    "message": f"Neo4j data processing completed for entire project {project_name}", "results": results}
        
        except Exception as e:
            logger.exception(f"Error during Neo4j data processing for entire project: {str(e)}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
    
    async def process_neo4j_data(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            task = self.async_task_adapter.send_task(
                'process_neo4j_data',
                args=[project_name, diagram_type]
            )
            return {
                "status": "processing",
                "message": f"Neo4j data processing started: {project_name}, {diagram_type}",
                "task_id": task.id
            }
        except Exception as e:
            logger.exception(f"Error during Neo4j data processing initiation: {str(e)}")
            return {"status": "error", "message": f"Error initiating Neo4j data processing: {str(e)}"}
    
    async def process_entire_project(self, project_name: str) -> Dict[str, Any]:
        try:
            task = self.async_task_adapter.send_task(
                'process_entire_project',
                args=[project_name]
            )
            return {
                "status": "processing",
                "message": f"Entire project Neo4j processing started: {project_name}",
                "task_id": task.id
            }
        except Exception as e:
            logger.exception(f"Error during entire project Neo4j processing initiation: {str(e)}")
            return {"status": "error", "message": f"Error initiating entire project Neo4j processing: {str(e)}"}
    
    async def monitor_task(self, task_id: str) -> Dict[str, Any]:
        try:
            return await self.async_task_adapter.monitor_task(task_id, self.update_processing_status)
        except Exception as e:
            logger.exception(f"Error monitoring task {task_id}: {str(e)}")
            return {"status": "error", "message": f"Error monitoring task: {str(e)}"}
    
    async def update_processing_status(self, status: Dict[str, Any]):
        from src.app_state import app_state
        app_state.processing_status = status
        logger.info(f"Task status updated: {status['status']}")
