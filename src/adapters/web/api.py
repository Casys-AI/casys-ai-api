
# src/adapters/web/api.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Any, Dict

from src.infrastructure.celery_app_state import CeleryAppState, celery_app_state
from src.infrastructure.dependencies import (
    get_project_manager,
    get_project_processing_service,
    get_neo4j_processing_service,
    get_neo4j_adapter,
    get_async_task_adapter
)
from src.infrastructure.app_state import app_state, AppState
from src.infrastructure.config import config

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application state...")
    try:
        # Initialisation des propriétés cached si nécessaire
        _ = app_state.project_manager
        _ = app_state.neo4j_adapter
        
        # Initialisation de CeleryAppState
        _ = celery_app_state.project_processing_service
        _ = celery_app_state.neo4j_processing_service
        
        logger.info("Application state initialized successfully.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.exception("Detailed error:")  # Ajoutez cette ligne pour plus de détails
    
    yield
    
    app_state.close_neo4j()
    logger.info("Application state cleaned up.")


app = FastAPI(title="SysML PLM API", lifespan=lifespan)
cors_config = config.get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config['allowed_origins'],
    allow_credentials=cors_config['allow_credentials'],
    allow_methods=cors_config['allow_methods'],
    allow_headers=cors_config['allow_headers'],
)


@app.get("/test-neo4j-connection")
async def test_neo4j_connection(neo4j_adapter=Depends(get_neo4j_adapter)) -> Dict[str, Any]:
    is_connected = neo4j_adapter.is_connected()
    return {
        "status": "connected" if is_connected else "disconnected",
        "message": "Neo4j connection successful" if is_connected else "Unable to connect to Neo4j"
    }


@app.post("/process/{project_name}")
async def process_project(
        project_name: str,
        project_processing_service=Depends(get_project_processing_service)
) -> Dict[str, Any]:
    try:
        return await project_processing_service.process_project(project_name)
    except Exception as e:
        logger.exception(f"Error starting project processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/{project_name}/{diagram_type}")
async def process_project_diagram(
        project_name: str,
        diagram_type: str,
        project_manager=Depends(get_project_manager),
        project_processing_service=Depends(get_project_processing_service)
) -> Dict[str, Any]:
    if diagram_type not in project_manager.get_diagram_types():
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")
    try:
        return await project_processing_service.process_project_diagram(project_name, diagram_type)
    except Exception as e:
        logger.exception(f"Error starting diagram processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract-json/{project_name}/{diagram_type}")
async def extract_json(
        project_name: str,
        diagram_type: str,
        project_manager=Depends(get_project_manager),
        project_processing_service=Depends(get_project_processing_service)
) -> Dict[str, Any]:
    if diagram_type not in project_manager.get_diagram_types():
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")
    try:
        return await project_processing_service.extract_json(project_name, diagram_type)
    except Exception as e:
        logger.exception(f"Error starting JSON extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-neo4j-data/{project_name}/{diagram_type}")
async def process_neo4j_data(
        project_name: str,
        diagram_type: str,
        project_manager=Depends(get_project_manager),
        neo4j_processing_service=Depends(get_neo4j_processing_service),
        neo4j_adapter=Depends(get_neo4j_adapter)
) -> Dict[str, Any]:
    if not neo4j_adapter.is_connected():
        return {"status": "error", "message": "Neo4j is not available. Please try again later."}
    if diagram_type not in project_manager.get_diagram_types():
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")
    try:
        return await neo4j_processing_service.process_neo4j_data(project_name, diagram_type)
    except Exception as e:
        logger.exception(f"Error starting Neo4j data processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/neo4j-process-project/{project_name}")
async def neo4j_process_project(
        project_name: str,
        neo4j_processing_service=Depends(get_neo4j_processing_service)
) -> Dict[str, Any]:
    try:
        return await neo4j_processing_service.process_entire_project(project_name)
    except Exception as e:
        logger.exception(f"Error starting entire project processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{task_id}")
async def get_task_status(
        task_id: str,
        async_task_adapter=Depends(get_async_task_adapter)
) -> Dict[str, Any]:
    try:
        return await async_task_adapter.get_task_status(task_id)
    except Exception as e:
        logger.exception(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_processing_status() -> Dict[str, Any]:
    return {
        "processing_status": app_state.processing_status,
        "service_status": app_state.get_service_status()
    }


@app.get("/")
async def root() -> Dict[str, str]:
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the SysML PLM API"}

