# src/application/services/project_processing_service.py

import json
import logging
from typing import Dict, Any

from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter
from src.adapters.web.document_adapter import DocumentAdapter
from src.adapters.web.entity_extraction_adapter import EntityExtractionAdapter
from src.adapters.web.openai_embedding_adapter import OpenAIEmbeddingAdapter
from src.adapters.web.rag_adapter import RAGAdapter
from src.application.services.document_service import DocumentService
from src.application.services.entity_extraction_service import EntityExtractionService
from src.application.services.project_management_service import ProjectManagementService
from src.application.services.rag_service import RAGService
from src.domain.ports.async_task_port import AsyncTaskPort

logger = logging.getLogger("uvicorn.error")


class ProjectProcessingService:
    def __init__(self, project_manager: ProjectManagementService, async_task_adapter: AsyncTaskPort):
        self.project_manager = project_manager
        config = self.project_manager.get_config()
        self.async_task_adapter = async_task_adapter
        self.embedding_service = OpenAIEmbeddingAdapter(config['openai']['api_key'])
        self.neo4j_adapter = Neo4jPersistenceAdapter(config)
        self.rag_adapter = RAGAdapter(config, self.embedding_service, self.neo4j_adapter)
        self.document_adapter = DocumentAdapter(config, self.rag_adapter.openai_chat)
        self.entity_extraction_adapter = EntityExtractionAdapter(self.rag_adapter.openai_chat)
        self.rag_service = RAGService(self.rag_adapter)
        self.document_service = DocumentService(self.document_adapter)
        self.entity_extraction_service = EntityExtractionService(self.entity_extraction_adapter)
    
    async def process_project(self, project_name: str) -> Dict[str, Any]:
        try:
            task = self.async_task_adapter.send_task(
                'process_project',
                args=[project_name]
            )
            return {
                "status": "processing",
                "message": f"Project processing started: {project_name}",
                "task_id": task.id
            }
        except Exception as e:
            logger.exception(f"Error during project processing initiation: {str(e)}")
            return {"status": "error", "message": f"Error initiating project processing: {str(e)}"}
    
    async def process_project_diagram(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            task = self.async_task_adapter.send_task(
                'process_project_diagram',
                args=[project_name, diagram_type]
            )
            return {
                "status": "processing",
                "message": f"Project diagram processing started: {project_name}, {diagram_type}",
                "task_id": task.id
            }
        except Exception as e:
            logger.exception(f"Error during project diagram processing initiation: {str(e)}")
            return {"status": "error", "message": f"Error initiating project diagram processing: {str(e)}"}
    
    async def extract_json(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            task = self.async_task_adapter.send_task(
                'extract_json',
                args=[project_name, diagram_type]
            )
            return {
                "status": "processing",
                "message": f"JSON extraction started: {project_name}, {diagram_type}",
                "task_id": task.id
            }
        except Exception as e:
            logger.exception(f"Error during JSON extraction initiation: {str(e)}")
            return {"status": "error", "message": f"Error initiating JSON extraction: {str(e)}"}
    
    def _process_project(self, project_name: str) -> Dict[str, Any]:
        try:
            self.project_manager.find_project(project_name)
            diagram_types = self.project_manager.get_diagram_types()
            
            summary = self._prepare_project_summary(project_name)
            
            results = []
            for diagram_type in diagram_types:
                result = self._process_diagram(project_name, diagram_type, summary)
                results.append(result)
            
            return {"status": "completed", "message": f"Project processing completed: {project_name}",
                    "results": results}
        except Exception as e:
            logger.exception(f"Une erreur est survenue lors du traitement du projet {project_name}")
            return {"status": "error", "message": f"Error during processing {project_name}: {str(e)}"}
    
    def _process_project_diagram(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            self.project_manager.find_project(project_name)
            summary = self._prepare_project_summary(project_name)
            result = self._process_diagram(project_name, diagram_type, summary)
            return result
        except Exception as e:
            logger.exception(f"Error during project diagram processing: {str(e)}")
            return {"status": "error", "message": f"Error during processing {project_name}, {diagram_type}: {str(e)}"}
    
    def _extract_json(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            diagram_content = self._read_diagram_content(project_name, diagram_type)
            entities = self.entity_extraction_service.extract_entities_and_relationships(
                diagram_content['mermaid_syntax'])
            entities_path = self.project_manager.get_project_entities_path(project_name, diagram_type)
            self.project_manager.save_entities_and_relationships(entities, entities_path)
            return {"status": "completed", "message": f"JSON extraction completed: {project_name}, {diagram_type}",
                    "entities": entities}
        except Exception as e:
            logger.exception(f"Error during JSON extraction: {str(e)}")
            return {"status": "error",
                    "message": f"Error during JSON extraction {project_name}, {diagram_type}: {str(e)}"}
    
    def _prepare_project_summary(self, project_name: str) -> str:
        input_path = self.project_manager.get_project_input_path(project_name)
        content = self.document_service.load_document(input_path)
        docs = self.document_service.split_text(content)
        return self.document_service.summarize_text_parallel(docs)
    
    def _read_diagram_content(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        output_path = self.project_manager.get_project_output_path(project_name, diagram_type)
        with open(output_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _process_diagram(self, project_name: str, diagram_type: str, summary: str) -> Dict[str, Any]:
        prompt_path = self.project_manager.get_project_prompt_path(project_name, diagram_type)
        prompt_template = self.project_manager.read_prompt_template(prompt_path)
        
        if not prompt_template:
            logger.error(
                f"Impossible de générer le diagramme {diagram_type} en raison d'une erreur de lecture du prompt")
            return {"status": "error", "message": f"Erreur de lecture du prompt pour {diagram_type}"}
        
        try:
            diagram_content = self.rag_service.generate_with_fallback(prompt_template, content=summary)
            
            diagram_data = {
                "project_name": project_name,
                "diagram_type": diagram_type,
                "mermaid_syntax": diagram_content
            }
            
            output_path = self.project_manager.get_project_output_path(project_name, diagram_type)
            self.project_manager.save_json(diagram_data, output_path)
            
            entities = self.entity_extraction_service.extract_entities_and_relationships(diagram_content)
            entities_path = self.project_manager.get_project_entities_path(project_name, diagram_type)
            self.project_manager.save_entities_and_relationships(entities, entities_path)
            
            return {"status": "completed", "message": f"Diagram processing completed: {project_name}, {diagram_type}"}
        except Exception as e:
            logger.exception(f"Error during diagram processing: {str(e)}")
            return {"status": "error", "message": f"Error during diagram processing: {str(e)}"}
    
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