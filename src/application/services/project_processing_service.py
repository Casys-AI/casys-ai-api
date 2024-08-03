import logging
from typing import Dict, Any

from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter
from src.adapters.web.rag_adapter import RAGAdapter
from src.adapters.web.document_adapter import DocumentAdapter
from src.adapters.web.entity_extraction_adapter import EntityExtractionAdapter
from src.application.services.project_management_service import ProjectManagementService
from src.application.services.rag_service import RAGService
from src.application.services.document_service import DocumentService
from src.application.services.entity_extraction_service import EntityExtractionService
from src.adapters.web.openai_embedding_adapter import OpenAIEmbeddingAdapter

logger = logging.getLogger("uvicorn.error")


class ProjectProcessingService:
    def __init__(self, project_manager: ProjectManagementService):
        self.project_manager = project_manager
        config = self.project_manager.get_config()
        self.embedding_service = OpenAIEmbeddingAdapter(config['openai']['api_key'])
        self.neo4j_adapter = Neo4jPersistenceAdapter(self.project_manager.config)
        self.rag_adapter = RAGAdapter(config, self.embedding_service, self.neo4j_adapter) #rajout ici à voir si ça ne pose pas des problèmes
        self.document_adapter = DocumentAdapter(config, self.rag_adapter.openai_chat)
        self.entity_extraction_adapter = EntityExtractionAdapter(self.rag_adapter.openai_chat)
        self.rag_service = RAGService(self.rag_adapter)
        self.document_service = DocumentService(self.document_adapter)
        self.entity_extraction_service = EntityExtractionService(self.entity_extraction_adapter)

    async def process_project(self, project_name: str) -> Dict[str, Any]:
        try:
            self.project_manager.find_project(project_name)  # Vérifier si le projet existe
            diagram_types = self.project_manager.get_diagram_types()

            summary = await self._prepare_project_summary(project_name)

            for diagram_type in diagram_types:
                await self._process_diagram(project_name, diagram_type, summary)

            return {"status": "completed", "message": f"Project processing completed: {project_name}"}
        except Exception as e:
            logger.exception(f"Une erreur est survenue lors du traitement du projet {project_name}")
            return {"status": "error", "message": f"Error during processing {project_name}: {str(e)}"}

    async def process_project_diagram(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            self.project_manager.find_project(project_name)  # Vérifier si le projet existe
            summary = await self._prepare_project_summary(project_name)
            await self._process_diagram(project_name, diagram_type, summary)
            return {"status": "completed",
                    "message": f"Project diagram processing completed: {project_name}, {diagram_type}"}
        except Exception as e:
            logger.exception(f"Error during project diagram processing: {str(e)}")
            return {"status": "error", "message": f"Error during processing {project_name}, {diagram_type}: {str(e)}"}

    async def extract_json(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            diagram_content = self._read_diagram_content(project_name, diagram_type)
            entities = self.entity_extraction_service.extract_entities_and_relationships(diagram_content)
            entities_path = self.project_manager.get_project_entities_path(project_name, diagram_type)
            self.project_manager.save_entities_and_relationships(entities, entities_path)
            return {"status": "completed", "message": f"JSON extraction completed: {project_name}, {diagram_type}"}
        except Exception as e:
            logger.exception(f"Error during JSON extraction: {str(e)}")
            return {"status": "error",
                    "message": f"Error during JSON extraction {project_name}, {diagram_type}: {str(e)}"}

    async def _prepare_project_summary(self, project_name: str) -> str:
        input_path = self.project_manager.get_project_input_path(project_name)
        content = self.document_service.load_document(input_path)
        docs = self.document_service.split_text(content)
        return self.document_service.summarize_text_parallel(docs)

    async def _process_diagram(self, project_name: str, diagram_type: str, summary: str) -> None:
        prompt_path = self.project_manager.get_project_prompt_path(project_name, diagram_type)
        prompt_template = self.project_manager.read_prompt_template(prompt_path)
        if not prompt_template:
            logger.error(
                f"Impossible de générer le diagramme {diagram_type} en raison d'une erreur de lecture du prompt")
            return

        diagram_content = self.rag_service.generate_with_fallback(prompt_template, content=summary)
        output_path = self.project_manager.get_project_output_path(project_name, diagram_type)
        self.project_manager.save_diagram(diagram_content, output_path)

        entities = self.entity_extraction_service.extract_entities_and_relationships(diagram_content)
        entities_path = self.project_manager.get_project_entities_path(project_name, diagram_type)
        self.project_manager.save_entities_and_relationships(entities, entities_path)

    def _read_diagram_content(self, project_name: str, diagram_type: str) -> str:
        output_path = self.project_manager.get_project_output_path(project_name, diagram_type)
        with open(output_path, 'r', encoding='utf-8') as f:
            return f.read()
