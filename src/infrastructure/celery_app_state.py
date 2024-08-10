from functools import cached_property
from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter
from src.adapters.web.rag_adapter import RAGAdapter
from src.application.factories.embedding_service_factory import EmbeddingServiceFactory
from src.application.factories.similarity_service_factory import SimilarityServiceFactory
from src.application.services.project_management_service import ProjectManagementService
from src.application.processing.project_processing_service import ProjectProcessingService
from src.application.processing.neo4j_processing_service import Neo4jProcessingService
from src.adapters.celery.celery_adapter import CeleryAdapter
from src.adapters.celery.celery_config import celery_app
from src.application.services.similarity_processing_service import SimilarityService
from src.infrastructure.config import config
import logging

logger = logging.getLogger("uvicorn.error")


class CeleryAppState:
    def __init__(self):
        self._similarity_service = None
        self._embedding_adapter = None
        self._processing_status = {"status": "idle", "message": "No processing has started yet"}
        self._config = config
        self._project_manager = ProjectManagementService()
        self._celery_adapter = CeleryAdapter(celery_app)
    
    @property
    def config(self):
        return self._config
    
    @cached_property
    def neo4j_adapter(self):
        return Neo4jPersistenceAdapter()
    
    @cached_property
    def embedding_adapter(self):
        if not self._embedding_adapter:
            self._embedding_adapter = EmbeddingServiceFactory.create_embedding_service(
                self.config.global_config.OPENAI_API_KEY)
        return self._embedding_adapter
    
    @cached_property
    def rag_adapter(self):
        return RAGAdapter(self.embedding_adapter, self.neo4j_adapter)
    
    @cached_property
    def similarity_service(self):
        if not self._similarity_service:
            self._similarity_service = SimilarityServiceFactory.create_similarity_service()
        return self._similarity_service
    
    @cached_property
    def project_processing_service(self):
        return ProjectProcessingService(self._project_manager, self._celery_adapter)
    
    @cached_property
    def neo4j_processing_service(self):
        return Neo4jProcessingService(
            self._project_manager,
            self.neo4j_adapter,
            self.similarity_service,
            self._celery_adapter
        )
    
    @property
    def processing_status(self):
        return self._processing_status
    
    @processing_status.setter
    def processing_status(self, value):
        self._processing_status = value


celery_app_state = CeleryAppState()