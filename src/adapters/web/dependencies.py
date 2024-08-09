from fastapi import Depends

from src.adapters.celery.celery_adapter import CeleryAdapter
from src.adapters.celery.celery_config import celery_app

from src.app_state import app_state
from src.application.services.neo4j_processing_service import Neo4jProcessingService
from src.application.services.project_management_service import ProjectManagementService
from src.application.services.project_processing_service import ProjectProcessingService
from src.application.services.similarity_processing_service import SimilarityService
from src.domain.ports.async_task_port import AsyncTaskPort
from src.domain.ports.embedding_adapter_protocol import EmbeddingAdapterProtocol
from src.domain.ports.neo4j_persistence_adapter_protocol import Neo4jPersistenceAdapterProtocol


def get_config():
    return app_state.config


def get_neo4j_adapter():
    return app_state.neo4j_adapter


def get_embedding_adapter():
    return app_state.embedding_adapter


def get_rag_adapter():
    return app_state.rag_adapter


def get_project_manager():
    return app_state.project_manager


def get_async_task_adapter():
    return CeleryAdapter(celery_app)


def get_similarity_service():
    return app_state.similarity_service


def get_project_processing_service(
        project_manager: ProjectManagementService = Depends(get_project_manager),
        async_task_adapter: AsyncTaskPort = Depends(get_async_task_adapter)
):
    return ProjectProcessingService(project_manager, async_task_adapter)


def get_neo4j_processing_service(
        project_manager: ProjectManagementService = Depends(get_project_manager),
        embedding_adapter: EmbeddingAdapterProtocol = Depends(get_embedding_adapter),
        neo4j_adapter: Neo4jPersistenceAdapterProtocol = Depends(get_neo4j_adapter),
        similarity_service: SimilarityService = Depends(get_similarity_service),
        async_task_adapter: AsyncTaskPort = Depends(get_async_task_adapter)
):
    return Neo4jProcessingService(
        project_manager,
        embedding_adapter,
        neo4j_adapter,
        similarity_service,
        async_task_adapter
    )
