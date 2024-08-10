#app_state
import logging
from functools import cached_property

from src.application.factories.embedding_service_factory import EmbeddingServiceFactory
from src.application.factories.similarity_service_factory import SimilarityServiceFactory
from src.infrastructure.config import config
from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter
from src.adapters.web.rag_adapter import RAGAdapter
from src.application.services.project_management_service import ProjectManagementService
from src.application.services.similarity_processing_service import SimilarityService

logger = logging.getLogger("uvicorn.error")


class AppState:
    def __init__(self):
        self.config = config
        self._project_manager = None
        self._neo4j_adapter = None
        self._embedding_adapter = None
        self._rag_adapter = None
        self._similarity_service = None
        self._processing_status = {"status": "idle", "message": "No processing has started yet"}
    
    @cached_property
    def project_manager(self):
        if not self._project_manager:
            self._project_manager = ProjectManagementService()
        return self._project_manager
    
    @cached_property
    def neo4j_adapter(self):
        if not self._neo4j_adapter:
            self._neo4j_adapter = Neo4jPersistenceAdapter()
        return self._neo4j_adapter
    
    @cached_property
    def embedding_adapter(self):
        if not self._embedding_adapter:
            self._embedding_adapter = EmbeddingServiceFactory.create_embedding_service(
                self.config.global_config.OPENAI_API_KEY)
        return self._embedding_adapter
    
    @cached_property
    def rag_adapter(self):
        if not self._rag_adapter:
            self._rag_adapter = RAGAdapter(self.embedding_adapter, self.neo4j_adapter)
        return self._rag_adapter
    
    @cached_property
    def similarity_service(self):
        if not self._similarity_service:
            self._similarity_service = SimilarityServiceFactory.create_similarity_service()
        return self._similarity_service
    
    @property
    def processing_status(self):
        return self._processing_status
    
    @processing_status.setter
    def processing_status(self, value):
        self._processing_status = value
    
    def close_neo4j(self):
        if self._neo4j_adapter:
            self._neo4j_adapter.close_neo4j()
    
    def get_service_status(self):
        return {
            "neo4j_adapter": self.neo4j_adapter.is_connected() if self._neo4j_adapter else False,
            "project_manager": self._project_manager is not None,
            "embedding_adapter": self._embedding_adapter is not None,
            "rag_adapter": self._rag_adapter is not None,
            "similarity_service": self._similarity_service is not None,
        }


app_state = AppState()