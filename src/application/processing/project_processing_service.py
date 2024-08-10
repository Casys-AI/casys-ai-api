import json
import logging
from typing import Dict, Any

from src.application.factories.embedding_service_factory import EmbeddingServiceFactory
from src.infrastructure.config import config
from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter
from src.adapters.web.document_adapter import DocumentAdapter
from src.adapters.web.entity_extraction_adapter import EntityExtractionAdapter
from src.adapters.web.rag_adapter import RAGAdapter
from src.application.services.document_service import DocumentService
from src.application.services.entity_extraction_service import EntityExtractionService
from src.application.services.project_management_service import ProjectManagementService
from src.application.services.rag_service import RAGService
from src.domain.ports.async_task_protocol import AsyncTaskProtocol

logger = logging.getLogger("uvicorn.error")


class ProjectProcessingService:
    def __init__(self, project_manager: ProjectManagementService, async_task_adapter: AsyncTaskProtocol):
        self.project_manager = project_manager
        self.async_task_adapter = async_task_adapter
        self.embedding_service = EmbeddingServiceFactory.create_embedding_service(config.global_config.OPENAI_API_KEY)
        self.neo4j_adapter = Neo4jPersistenceAdapter()
        self.rag_adapter = RAGAdapter(self.embedding_service, self.neo4j_adapter)
        self.document_adapter = DocumentAdapter(self.rag_adapter.openai_chat)
        self.entity_extraction_adapter = EntityExtractionAdapter(self.rag_adapter.openai_chat)
        self.rag_service = RAGService(self.rag_adapter)
        self.document_service = DocumentService(self.document_adapter)
        self.entity_extraction_service = EntityExtractionService(self.entity_extraction_adapter)
    
    async def process_project(self, project_name: str) -> Dict[str, Any]:
        return await self._send_task('process_project', project_name, "Project processing")
    
    async def process_project_diagram(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        return await self._send_task('process_project_diagram', project_name, f"Project diagram processing",
                                     diagram_type)
    
    async def extract_json(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        return await self._send_task('extract_json', project_name, "JSON extraction", diagram_type)
    
    async def _send_task(self, task_name: str, project_name: str, operation: str, diagram_type: str = None) -> Dict[
        str, Any]:
        try:
            args = [project_name] if diagram_type is None else [project_name, diagram_type]
            task = self.async_task_adapter.send_task(task_name, args=args)
            return {
                "status": "processing",
                "message": f"{operation} started: {project_name}" + (f", {diagram_type}" if diagram_type else ""),
                "task_id": task.id
            }
        except Exception as e:
            logger.exception(f"Error during {operation.lower()} initiation: {str(e)}")
            return {"status": "error", "message": f"Error initiating {operation.lower()}: {str(e)}"}
    
    def _process_project(self, project_name: str) -> Dict[str, Any]:
        try:
            self.project_manager.find_project(project_name)
            diagram_types = self.project_manager.get_diagram_types()
            summary = self._prepare_project_summary(project_name)
            results = [self._process_diagram(project_name, diagram_type, summary) for diagram_type in diagram_types]
            return {"status": "completed", "message": f"Project processing completed: {project_name}",
                    "results": results}
        except Exception as e:
            logger.exception(f"Error occurred during processing of project {project_name}")
            return {"status": "error", "message": f"Error during processing {project_name}: {str(e)}"}
    
    def _process_project_diagram(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            self.project_manager.find_project(project_name)
            summary = self._prepare_project_summary(project_name)
            return self._process_diagram(project_name, diagram_type, summary)
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
            logger.error(f"Unable to generate diagram {diagram_type} due to prompt reading error")
            return {"status": "error", "message": f"Error reading prompt for {diagram_type}"}
        
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
        from src.infrastructure.app_state import app_state
        app_state.processing_status = status
        logger.info(f"Task status updated: {status['status']}")