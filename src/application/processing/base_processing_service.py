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

#todo à implémenter pour centraliser la logique de processing
class BaseProcessingService:
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
