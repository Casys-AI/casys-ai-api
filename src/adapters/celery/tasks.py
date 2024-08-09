#src/adapters/celery/tasks.py
import logging
from typing import Dict, Any
from celery.exceptions import MaxRetriesExceededError
from src.adapters.celery.celery_config import celery_app
from src.adapters.web.dependencies import (
    get_project_manager, get_async_task_adapter, get_embedding_adapter,
    get_neo4j_adapter, get_similarity_service, get_neo4j_processing_service,
    get_project_processing_service
)

logger = logging.getLogger("uvicorn.error")

# Initialize dependencies
project_manager = get_project_manager()
async_task_adapter = get_async_task_adapter()
embedding_adapter = get_embedding_adapter()
neo4j_adapter = get_neo4j_adapter()
similarity_service = get_similarity_service()

def handle_task_error(task, exc, task_id, args, kwargs, einfo):
    logger.error(f"Task {task.name}[{task_id}] failed: {exc}")
    raise exc

@celery_app.task(name='process_project', bind=True, max_retries=3, on_failure=handle_task_error)
def process_project_task(self, project_name: str) -> Dict[str, Any]:
    logger.info(f"Starting process_project task for project: {project_name}")
    try:
        service = get_project_processing_service()
        result = service._process_project(project_name)
        logger.info(f"Completed process_project task for project: {project_name}")
        return result
    except Exception as exc:
        logger.exception(f"Error in process_project task for project: {project_name}")
        self.retry(exc=exc)

@celery_app.task(name='process_project_diagram', bind=True, max_retries=3, on_failure=handle_task_error)
def process_project_diagram_task(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
    logger.info(f"Starting process_project_diagram task for project: {project_name}, diagram: {diagram_type}")
    try:
        service = get_project_processing_service()
        result = service._process_project_diagram(project_name, diagram_type)
        logger.info(f"Completed process_project_diagram task for project: {project_name}, diagram: {diagram_type}")
        return result
    except Exception as exc:
        logger.exception(f"Error in process_project_diagram task for project: {project_name}, diagram: {diagram_type}")
        self.retry(exc=exc)

@celery_app.task(name='extract_json', bind=True, max_retries=3, on_failure=handle_task_error)
def extract_json_task(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
    logger.info(f"Starting extract_json task for project: {project_name}, diagram: {diagram_type}")
    try:
        service = get_project_processing_service()
        result = service._extract_json(project_name, diagram_type)
        logger.info(f"Completed extract_json task for project: {project_name}, diagram: {diagram_type}")
        return result
    except Exception as exc:
        logger.exception(f"Error in extract_json task for project: {project_name}, diagram: {diagram_type}")
        self.retry(exc=exc)

@celery_app.task(name='process_neo4j_data', bind=True, max_retries=3, on_failure=handle_task_error)
def process_neo4j_data_task(self, project_name: str, diagram_type: str):
    logger.info(f"Starting process_neo4j_data task for project: {project_name}, diagram: {diagram_type}")
    try:
        service = get_neo4j_processing_service()
        result = service._process_neo4j_data(project_name, diagram_type)
        logger.info(f"Completed process_neo4j_data task for project: {project_name}, diagram: {diagram_type}")
        return result
    except Exception as exc:
        logger.exception(f"Error in process_neo4j_data task for project: {project_name}, diagram: {diagram_type}")
        self.retry(exc=exc)

@celery_app.task(name='process_entire_project', bind=True, max_retries=3, on_failure=handle_task_error)
def process_entire_project_task(self, project_name: str):
    logger.info(f"Starting process_entire_project task for project: {project_name}")
    try:
        service = get_neo4j_processing_service()
        result = service._process_entire_project(project_name)
        logger.info(f"Completed process_entire_project task for project: {project_name}")
        return result
    except Exception as exc:
        logger.exception(f"Error in process_entire_project task for project: {project_name}")
        self.retry(exc=exc)