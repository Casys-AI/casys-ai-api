# src/app_state.py

import logging
from functools import cached_property

from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter
from src.adapters.web.openai_embedding_adapter import OpenAIEmbeddingAdapter
from src.adapters.web.rag_adapter import RAGAdapter
from src.application.services.project_management_service import ProjectManagementService
from src.application.services.similarity_processing_service import SimilarityService
from src.utils.config import GLOBAL_CONFIG

logger = logging.getLogger("uvicorn.error")


class AppState:
    def __init__(self):
        self.global_config = GLOBAL_CONFIG
        self.config = None
        self._project_manager = None
        self._neo4j_adapter = None
        self._embedding_adapter = None
        self._rag_adapter = None
        self._similarity_service = None
        self._neo4j_processing_service = None
        self._project_processing_service = None
        self._processing_status = {"status": "idle", "message": "No processing has started yet"}
    
    @cached_property
    def project_manager(self):
        if not self._project_manager:
            self._project_manager = ProjectManagementService(r"config.yaml")
            self.config = self._project_manager.get_config()
        return self._project_manager
    
    @cached_property
    def neo4j_adapter(self):
        if not self._neo4j_adapter:
            self._neo4j_adapter = Neo4jPersistenceAdapter(self.global_config)
            if not self._neo4j_adapter.is_connected():
                logger.warning("Unable to connect to Neo4j. Some features may be limited.")
            else:
                logger.info("Neo4j connection successful")
        return self._neo4j_adapter
    
    @cached_property
    def embedding_adapter(self):
        if not self._embedding_adapter:
            self._embedding_adapter = OpenAIEmbeddingAdapter(api_key=self.global_config["openai"]["api_key"])
        return self._embedding_adapter
    
    @cached_property
    def rag_adapter(self):
        if not self._rag_adapter:
            self._rag_adapter = RAGAdapter(self.global_config, self.embedding_adapter, self.neo4j_adapter)
        return self._rag_adapter
    
    @cached_property
    def similarity_service(self):
        if not self._similarity_service:
            self._similarity_service = SimilarityService(self.global_config)
        return self._similarity_service
    
    @cached_property
    def neo4j_processing_service(self):
        if not self._neo4j_processing_service:
            from src.application.services.neo4j_processing_service import Neo4jProcessingService
            self._neo4j_processing_service = Neo4jProcessingService(
                self.project_manager,
                self.embedding_adapter,
                self.neo4j_adapter,
                self.similarity_service
            )
        return self._neo4j_processing_service
    
    @cached_property
    def project_processing_service(self):
        if not self._project_processing_service:
            from src.application.services.project_processing_service import ProjectProcessingService
            self._project_processing_service = ProjectProcessingService(self.project_manager)
        return self._project_processing_service
    
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
            "neo4j_processing_service": self._neo4j_processing_service is not None,
            "project_processing_service": self._project_processing_service is not None,
            
        }


app_state = AppState()
