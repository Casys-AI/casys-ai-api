#src/adapters/web/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Any, Dict

from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter
from src.adapters.web.openai_embedding_adapter import OpenAIEmbeddingAdapter
from src.adapters.web.process_projects import load_config
from src.application.services.create_diagram_service import CreateDiagramService
from src.adapters.persistence.file_diagram_repository_adapter import FileDiagramRepositoryAdapter
from src.application.services.project_processing_service import ProjectProcessingService
from src.application.services.neo4j_processing_service import Neo4jProcessingService

logger = logging.getLogger("uvicorn.error")

config = None
diagram_service = None
neo4j_adapter = None
processing_status = {"status": "idle", "message": "No processing has started yet"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes services and shuts them down.

    :param app: The FastAPI instance.
    :return: Context manager that yields control to the application after services initialization and before shutting down.

    """
    global config, diagram_service, neo4j_adapter
    logger.info("Initializing services...")
    try:
        config = load_config("config.yaml")
        file_repository = FileDiagramRepositoryAdapter(directory="diagrams")
        diagram_service = CreateDiagramService(repository=file_repository)

        neo4j_adapter = Neo4jPersistenceAdapter(config)
        OpenAIEmbeddingAdapter(config['openai']['api_key'])

        if neo4j_adapter.is_connected():
            logger.info("Neo4j connection successful")
        else:
            logger.warning("Unable to connect to Neo4j. Some features may be limited.")

        logger.info("Services initialized successfully.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")

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
    if not config or not diagram_service:
        raise HTTPException(status_code=500, detail="Services not initialized")

    try:
        result = await ProjectProcessingService.process_project(config, diagram_service, project_name)
        processing_status = result
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during project processing: {str(e)}")
        processing_status = {"status": "error", "message": f"Error during processing {project_name}: {str(e)}"}
        return {"status": "error", "message": str(e)}

@app.post("/process/{project_name}/{diagram_type}")
async def process_project_diagram(project_name: str, diagram_type: str) -> Dict[str, Any]:
    global processing_status
    if not config or not diagram_service:
        raise HTTPException(status_code=500, detail="Services not initialized")

    if diagram_type not in config['diagram_types']:
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")

    try:
        result = await ProjectProcessingService.process_project_diagram(config, diagram_service, project_name, diagram_type)
        processing_status = result
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during project diagram processing: {str(e)}")
        processing_status = {"status": "error", "message": f"Error during processing {project_name}, {diagram_type}: {str(e)}"}
        return {"status": "error", "message": str(e)}

@app.post("/extract-json/{project_name}/{diagram_type}")
async def extract_json(project_name: str, diagram_type: str) -> Dict[str, Any]:
    global processing_status
    if not config or not diagram_service:
        raise HTTPException(status_code=500, detail="Services not initialized")

    if diagram_type not in config['diagram_types']:
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")

    try:
        result = await ProjectProcessingService.extract_json(config, diagram_service, project_name, diagram_type)
        processing_status = result
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during JSON extraction: {str(e)}")
        processing_status = {"status": "error", "message": f"Error during JSON extraction: {str(e)}"}
        return {"status": "error", "message": str(e)}

@app.post("/process-neo4j-data/{project_name}/{diagram_type}")
async def process_neo4j_data(project_name: str, diagram_type: str) -> Dict[str, Any]:
    global processing_status
    if not config or not neo4j_adapter:
        raise HTTPException(status_code=500, detail="Services not initialized")

    if diagram_type not in config['diagram_types']:
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")

    try:
        result = await Neo4jProcessingService.process_neo4j_data(neo4j_adapter, project_name, diagram_type)
        processing_status = result
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