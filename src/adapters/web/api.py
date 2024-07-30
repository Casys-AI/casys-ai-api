from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Any, Dict

from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter
from src.adapters.web.openai_embedding_adapter import OpenAIEmbeddingAdapter
from src.application.services.project_management_service import ProjectManagementService
from src.application.services.create_diagram_service import CreateDiagramService
from src.adapters.persistence.file_diagram_repository_adapter import FileDiagramRepositoryAdapter
from src.application.services.project_processing_service import ProjectProcessingService
from src.application.services.neo4j_processing_service import Neo4jProcessingService

logger = logging.getLogger("uvicorn.error")

project_manager = None
project_processing_service = None
diagram_service = None
neo4j_adapter = None
processing_status = {"status": "idle", "message": "No processing has started yet"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global project_processing_service, diagram_service, neo4j_adapter
    logger.info("Initializing services...")
    try:
        project_processing_service = ProjectProcessingService("config.yaml")
        if not project_processing_service or not project_processing_service.config:
            raise ValueError("Failed to initialize ProjectProcessingService or load configuration")

        file_repository = FileDiagramRepositoryAdapter(directory="diagrams")
        diagram_service = CreateDiagramService(repository=file_repository)

        neo4j_adapter = Neo4jPersistenceAdapter(project_processing_service.config)

        if neo4j_adapter.is_connected():
            logger.info("Neo4j connection successful")
        else:
            logger.warning("Unable to connect to Neo4j. Some features may be limited.")

        logger.info("Services initialized successfully.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

    yield

    logger.info("Shutting down...")
    if neo4j_adapter:
        neo4j_adapter.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/process/{project_name}")
async def process_project(project_name: str) -> Dict[str, Any]:
    global processing_status
    if not project_processing_service:
        raise HTTPException(status_code=500, detail="Services not initialized")

    try:
        result = await project_processing_service.process_project(project_name)
        processing_status = result
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during project processing: {str(e)}")
        processing_status = {"status": "error", "message": f"Error during processing {project_name}: {str(e)}"}
        return {"status": "error", "message": str(e)}


@app.post("/process/{project_name}/{diagram_type}")
async def process_project_diagram(project_name: str, diagram_type: str) -> Dict[str, Any]:
    global processing_status
    if not project_processing_service:
        raise HTTPException(status_code=500, detail="Services not initialized")

    if diagram_type not in project_processing_service.config['diagram_types']:
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")

    try:
        result = await project_processing_service.process_project_diagram(project_name, diagram_type)
        processing_status = result
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during project diagram processing: {str(e)}")
        processing_status = {"status": "error", "message": f"Error during processing {project_name}, {diagram_type}: {str(e)}"}
        return {"status": "error", "message": str(e)}


@app.post("/extract-json/{project_name}/{diagram_type}")
async def extract_json(project_name: str, diagram_type: str) -> Dict[str, Any]:
    global processing_status
    if not project_processing_service:
        raise HTTPException(status_code=500, detail="Services not initialized")

    if diagram_type not in project_processing_service.config['diagram_types']:
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")

    try:
        result = await project_processing_service.extract_json(project_name, diagram_type)
        processing_status = result
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during JSON extraction: {str(e)}")
        processing_status = {"status": "error", "message": f"Error during JSON extraction: {str(e)}"}
        return {"status": "error", "message": str(e)}


@app.post("/process-neo4j-data/{project_name}/{diagram_type}")
async def process_neo4j_data(project_name: str, diagram_type: str) -> Dict[str, Any]:
    global processing_status
    if not neo4j_adapter or not project_processing_service:
        logger.error("Services not initialized")
        raise HTTPException(status_code=500, detail="Services not initialized")

    if diagram_type not in project_processing_service.config['diagram_types']:
        logger.error(f"Invalid diagram type: {diagram_type}")
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")

    try:
        logger.info(f"Processing Neo4j data for project: {project_name}, diagram: {diagram_type}")
        result = await Neo4jProcessingService.process_neo4j_data(neo4j_adapter, project_name, diagram_type)
        processing_status = result
        logger.info(f"Neo4j data processing completed: {result}")
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during Neo4j data processing: {str(e)}")
        processing_status = {"status": "error", "message": f"Error during Neo4j data processing: {str(e)}"}
        return {"status": "error", "message": str(e)}


@app.get("/status")
async def get_processing_status() -> Dict[str, Any]:
    return processing_status


@app.get("/")
async def root() -> Dict[str, str]:
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the SysML PLM API"}