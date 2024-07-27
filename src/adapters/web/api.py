from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.adapters.web.process_projects import load_config, process_single_project, process_single_project_diagram
from src.adapters.web.rag_adapter import RAGAdapter
from src.application.services.create_diagram_service import CreateDiagramService
from src.adapters.persistence.file_diagram_repository_adapter import FileDiagramRepositoryAdapter
import logging
from typing import Any, Dict
import asyncio

logger = logging.getLogger("uvicorn.error")

config = None
service = None
processing_status = {"status": "idle", "message": "No processing has started yet"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global config, service
    logger.info("Initializing services...")
    try:
        config = load_config("config.yaml")
        repository = FileDiagramRepositoryAdapter(directory="diagrams")
        service = CreateDiagramService(repository=repository)

        # Vérifiez la connexion Neo4j
        rag_adapter = RAGAdapter(config)
        if rag_adapter.is_neo4j_connected():
            logger.info("Neo4j connection successful")
        else:
            logger.warning("Unable to connect to Neo4j. Some features may be limited.")

        logger.info("Services initialized successfully.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Ne levez pas d'exception ici, permettez à l'application de démarrer même en cas d'erreur

    yield

    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def process_project_task(config: Dict[str, Any], service: Any, project_name: str):
    global processing_status
    processing_status = {"status": "processing", "message": f"Processing project: {project_name}"}
    try:
        logger.info(f"Starting processing for project: {project_name}")
        process_single_project(config, service, project_name)
        logger.info(f"Project processing completed successfully: {project_name}")
        processing_status = {"status": "completed", "message": f"Project processing completed: {project_name}"}
    except Exception as e:
        logger.exception(f"Error during project processing: {str(e)}")
        processing_status = {"status": "error", "message": f"Error during processing {project_name}: {str(e)}"}


async def process_project_diagram_task(config: Dict[str, Any], service: Any, project_name: str, diagram_type: str):
    global processing_status
    processing_status = {"status": "processing", "message": f"Processing {diagram_type} diagram for project: {project_name}"}
    try:
        logger.info(f"Starting processing for project: {project_name}, diagram: {diagram_type}")
        process_single_project_diagram(config, service, project_name, diagram_type)
        logger.info(f"Project diagram processing completed successfully: {project_name}, {diagram_type}")
        processing_status = {"status": "completed", "message": f"Project diagram processing completed: {project_name}, {diagram_type}"}
    except Exception as e:
        logger.exception(f"Error during project diagram processing: {str(e)}")
        processing_status = {"status": "error", "message": f"Error during processing {project_name}, {diagram_type}: {str(e)}"}


@app.post("/process/{project_name}")
async def process_project(project_name: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    logger.info(f"Received request to process project: {project_name}")
    if not config or not service:
        logger.error("Services not initialized")
        raise HTTPException(status_code=500, detail="Services not initialized")

    try:
        logger.info(f"Starting processing for project {project_name} in background")
        asyncio.create_task(process_project_task(config, service, project_name))
        logger.info("Background task added successfully")
        return {"status": "success", "message": f"Project processing started for {project_name}"}
    except Exception as e:
        logger.exception(f"Error during project processing: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/process/{project_name}/{diagram_type}")
async def process_project_diagram(project_name: str, diagram_type: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    logger.info(f"Received request to process project: {project_name}, diagram: {diagram_type}")
    if not config or not service:
        logger.error("Services not initialized")
        raise HTTPException(status_code=500, detail="Services not initialized")

    if diagram_type not in config['diagram_types']:
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")

    try:
        logger.info(f"Starting processing for project {project_name}, diagram {diagram_type} in background")
        await asyncio.create_task(process_project_diagram_task(config, service, project_name, diagram_type))
        logger.info("Background task added successfully")
        return {"status": "success", "message": f"Project diagram processing started for {project_name}, {diagram_type}"}
    except Exception as e:
        logger.exception(f"Error during project diagram processing: {str(e)}")
        return {"status": "error", "message": str(e)}

# src/adapters/web/api.py

@app.post("/extract-json/{project_name}/{diagram_type}")
async def extract_json(project_name: str, diagram_type: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    logger.info(f"Received request to extract JSON for project: {project_name}, diagram: {diagram_type}")
    if not config or not service:
        logger.error("Services not initialized")
        raise HTTPException(status_code=500, detail="Services not initialized")

    if diagram_type not in config['diagram_types']:
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")

    try:
        logger.info(f"Starting JSON extraction for project {project_name}, diagram {diagram_type} in background")
        await asyncio.create_task(extract_json_task(config, service, project_name, diagram_type))
        logger.info("Background task added successfully")
        return {"status": "success", "message": f"JSON extraction started for {project_name}, {diagram_type}"}
    except Exception as e:
        logger.exception(f"Error during JSON extraction: {str(e)}")
        return {"status": "error", "message": str(e)}


async def extract_json_task(config: Dict[str, Any], service: Any, project_name: str, diagram_type: str):
    global processing_status
    processing_status = {"status": "processing", "message": f"Extracting JSON for {diagram_type} diagram of project: {project_name}"}
    try:
        logger.info(f"Starting JSON extraction for project: {project_name}, diagram: {diagram_type}")
        process_single_project_diagram(config, service, project_name, diagram_type, extract_json_only=True)
        logger.info(f"JSON extraction completed successfully: {project_name}, {diagram_type}")
        processing_status = {"status": "completed", "message": f"JSON extraction completed: {project_name}, {diagram_type}"}
    except Exception as e:
        logger.exception(f"Error during JSON extraction: {str(e)}")
        processing_status = {"status": "error", "message": f"Error during JSON extraction {project_name}, {diagram_type}: {str(e)}"}


@app.get("/status")
async def get_processing_status() -> Dict[str, Any]:
    return processing_status


@app.get("/")
async def root() -> Dict[str, str]:
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the SysML PLM API"}