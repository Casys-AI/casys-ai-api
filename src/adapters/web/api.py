from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Any, Dict

from src.adapters.web.dependencies import get_project_manager, get_project_processing_service, get_neo4j_processing_service, \
    get_neo4j_adapter
from app_state import app_state

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application state...")
    try:
        # Trigger the loading of config and minimal initialization
        app_state.project_manager  # This will trigger the loading of config
        logger.info("Application state initialized successfully.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
    
    yield
    
    # Cleanup resources
    app_state.close()
    logger.info("Application state cleaned up.")

app = FastAPI(title="SysML PLM API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        result = await project_processing_service.process_project(project_name)
        app_state.processing_status = result
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during project processing: {str(e)}")
        app_state.processing_status = {"status": "error", "message": f"Error during processing {project_name}: {str(e)}"}
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
        result = await project_processing_service.process_project_diagram(project_name, diagram_type)
        app_state.processing_status = result
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during project diagram processing: {str(e)}")
        app_state.processing_status = {"status": "error",
                                       "message": f"Error during processing {project_name}, {diagram_type}: {str(e)}"}
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
        result = await project_processing_service.extract_json(project_name, diagram_type)
        app_state.processing_status = result
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during JSON extraction: {str(e)}")
        app_state.processing_status = {"status": "error", "message": f"Error during JSON extraction: {str(e)}"}
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
        logger.info(f"Processing Neo4j data for project: {project_name}, diagram: {diagram_type}")
        result = await neo4j_processing_service.process_neo4j_data(project_name, diagram_type)
        app_state.processing_status = result
        logger.info(f"Neo4j data processing completed: {result}")
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during Neo4j data processing: {str(e)}")
        app_state.processing_status = {"status": "error", "message": f"Error during Neo4j data processing: {str(e)}"}
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-entire-project/{project_name}")
async def process_entire_project(
        project_name: str,
        neo4j_processing_service=Depends(get_neo4j_processing_service)
) -> Dict[str, Any]:
    try:
        logger.info(f"Processing entire project: {project_name}")
        result = await neo4j_processing_service.process_entire_project(project_name)
        app_state.processing_status = result
        logger.info(f"Entire project processing completed: {result}")
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during entire project processing: {str(e)}")
        app_state.processing_status = {"status": "error",
                                       "message": f"Error during entire project processing: {str(e)}"}
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