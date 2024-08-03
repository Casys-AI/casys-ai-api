from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Any, Dict

from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter
from src.adapters.web.openai_embedding_adapter import OpenAIEmbeddingAdapter
from src.application.services.project_management_service import ProjectManagementService
from src.application.services.create_diagram_service import CreateDiagramService
from src.adapters.persistence.file_diagram_repository_adapter import FileDiagramRepositoryAdapter
from src.application.services.neo4j_processing_service import Neo4jProcessingService
from src.application.services.project_processing_service import ProjectProcessingService
from src.application.services.similarity_processing_service import SimilarityService

logger = logging.getLogger("uvicorn.error")


class AppState:
    def __init__(self):
        self.project_manager = None
        self.project_processing_service = None
        self.diagram_service = None
        self.neo4j_adapter = None
        self.neo4j_processing_service = None
        self.embedding_adapter = None
        self.similarity_service = None
        self.processing_status = {"status": "idle", "message": "No processing has started yet"}


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing services...")
    try:
        app_state.project_manager = ProjectManagementService(r"C:\Users\erpes\PycharmProjects\SysML_PLM\config.yaml")
        config = app_state.project_manager.get_config()

        file_repository = FileDiagramRepositoryAdapter(directory="diagrams")
        app_state.diagram_service = CreateDiagramService(repository_adapter=file_repository)
        
        app_state.neo4j_adapter = Neo4jPersistenceAdapter(config)
        if not app_state.neo4j_adapter.is_connected():
            logger.warning("Unable to connect to Neo4j. Some features may be limited.")
        else:
            logger.info("Neo4j connection successful")

        app_state.embedding_adapter = OpenAIEmbeddingAdapter(api_key=config["openai"]["api_key"])
        app_state.similarity_service = SimilarityService(config)
        app_state.neo4j_processing_service = Neo4jProcessingService(
            app_state.project_manager,
            app_state.embedding_adapter,
            app_state.neo4j_adapter,
            app_state.similarity_service
        )
        app_state.project_processing_service = ProjectProcessingService(app_state.project_manager)

        logger.info("Services initialized successfully.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Ne pas lever d'exception ici, permettre à l'application de démarrer même en cas d'erreur
    
    yield
    
    logger.info("Shutting down...")
    if app_state.neo4j_adapter:
        app_state.neo4j_adapter.close()


app = FastAPI(title="SysML PLM API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_project_manager():
    if app_state.project_manager is None:
        raise HTTPException(status_code=500, detail="Project manager not initialized")
    return app_state.project_manager


@app.get("/test-neo4j-connection")
async def test_neo4j_connection() -> Dict[str, Any]:
    if not app_state.neo4j_adapter:
        raise HTTPException(status_code=500, detail="Neo4j adapter not initialized")
    is_connected = app_state.neo4j_adapter.is_connected()
    return {
        "status": "connected" if is_connected else "disconnected",
        "message": "Neo4j connection successful" if is_connected else "Unable to connect to Neo4j"
    }


@app.post("/process/{project_name}")
async def process_project(project_name: str) -> Dict[str, Any]:
    if not app_state.project_processing_service:
        raise HTTPException(status_code=500, detail="Project processing service not initialized")
    try:
        result = await app_state.project_processing_service.process_project(project_name)
        app_state.processing_status = result
        return {"status": "success", "message": result['message']}
    except Exception as e:
        logger.exception(f"Error during project processing: {str(e)}")
        app_state.processing_status = {"status": "error",
                                       "message": f"Error during processing {project_name}: {str(e)}"}
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/{project_name}/{diagram_type}")
async def process_project_diagram(
        project_name: str,
        diagram_type: str,
        project_manager: ProjectManagementService = Depends(get_project_manager)
) -> Dict[str, Any]:
    if not app_state.project_processing_service:
        raise HTTPException(status_code=500, detail="Project processing service not initialized")
    if diagram_type not in project_manager.get_diagram_types():
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")
    try:
        result = await app_state.project_processing_service.process_project_diagram(project_name, diagram_type)
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
        project_manager: ProjectManagementService = Depends(get_project_manager)
) -> Dict[str, Any]:
    if not app_state.project_processing_service:
        raise HTTPException(status_code=500, detail="Project processing service not initialized")
    if diagram_type not in project_manager.get_diagram_types():
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")
    try:
        result = await app_state.project_processing_service.extract_json(project_name, diagram_type)
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
        project_manager: ProjectManagementService = Depends(get_project_manager)
) -> Dict[str, Any]:
    if not app_state.neo4j_adapter.is_connected():
        return {"status": "error", "message": "Neo4j is not available. Please try again later."}
    if diagram_type not in project_manager.get_diagram_types():
        raise HTTPException(status_code=400, detail=f"Invalid diagram type: {diagram_type}")
    try:
        logger.info(f"Processing Neo4j data for project: {project_name}, diagram: {diagram_type}")
        result = await app_state.neo4j_processing_service.process_neo4j_data(project_name, diagram_type)
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
        project_manager: ProjectManagementService = Depends(get_project_manager)
) -> Dict[str, Any]:
    if not app_state.neo4j_processing_service:
        raise HTTPException(status_code=500, detail="Neo4j processing service not initialized")
    try:
        logger.info(f"Processing entire project: {project_name}")
        result = await app_state.neo4j_processing_service.process_entire_project(project_name)
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
    return app_state.processing_status


@app.get("/")
async def root() -> Dict[str, str]:
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the SysML PLM API"}
