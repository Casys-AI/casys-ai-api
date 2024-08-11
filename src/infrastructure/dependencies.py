#src/infrastructure/dependencies.py
from fastapi import Depends
from src.infrastructure.app_state import app_state
from src.application.processing.project_processing_service import ProjectProcessingService
from src.application.processing.neo4j_processing_service import Neo4jProcessingService
from src.adapters.celery.celery_adapter import CeleryAdapter
from src.adapters.celery.celery_config import celery_app


#découpler les dépendances de celery et de l'app
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


def get_similarity_service():
    return app_state.similarity_service


def get_async_task_adapter():
    return CeleryAdapter(celery_app)


def get_project_processing_service(
        project_manager=Depends(get_project_manager),
        async_task_adapter=Depends(get_async_task_adapter)
):
    return ProjectProcessingService(project_manager, async_task_adapter)


def get_neo4j_processing_service(
        project_manager=Depends(get_project_manager),
        neo4j_adapter=Depends(get_neo4j_adapter),
        similarity_service=Depends(get_similarity_service),
        async_task_adapter=Depends(get_async_task_adapter)
):
    return Neo4jProcessingService(
        project_manager,
        neo4j_adapter,
        similarity_service,
        async_task_adapter
    )
