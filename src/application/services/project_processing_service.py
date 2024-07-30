import logging
from typing import Dict, Any
from src.application.services.project_management_service import ProjectManagementService
from src.adapters.web.rag_adapter import RAGAdapter
from src.adapters.web.document_adapter import DocumentAdapter
from src.adapters.web.entity_extraction_adapter import EntityExtractionAdapter
from src.application.services.rag_service import RAGService
from src.application.services.document_service import DocumentService
from src.application.services.entity_extraction_service import EntityExtractionService
from src.adapters.web.openai_embedding_adapter import OpenAIEmbeddingAdapter

logger = logging.getLogger(__name__)


class ProjectProcessingService:
    def __init__(self, config_path: str):
        self.project_manager = ProjectManagementService(config_path)
        self.config = self.project_manager.get_config()
        self.embedding_service = OpenAIEmbeddingAdapter(self.config['openai']['api_key'])

    async def process_project(self, project_name: str) -> Dict[str, Any]:
        try:
            project, project_type = self.project_manager.find_project(project_name)

            rag_adapter = RAGAdapter(self.config, self.embedding_service)
            document_adapter = DocumentAdapter(self.config, rag_adapter.openai_chat)
            entity_extraction_adapter = EntityExtractionAdapter(rag_adapter.openai_chat)

            rag_service = RAGService(rag_adapter)
            document_service = DocumentService(document_adapter)
            entity_extraction_service = EntityExtractionService(entity_extraction_adapter)

            file_paths = self.project_manager.get_file_paths(project_type, project['name'])
            content = document_service.load_document(project['path'])
            docs = document_service.split_text(content)
            summary = document_service.summarize_text_parallel(docs)

            for diagram_type in self.config['diagram_types']:
                prompt_template = self.project_manager.read_prompt_template(file_paths[diagram_type]['prompt'])
                if not prompt_template:
                    logger.error(
                        f"Impossible de générer le diagramme {diagram_type} en raison d'une erreur de lecture du prompt")
                    continue

                diagram_content = rag_service.generate_with_fallback(prompt_template, content=summary)
                self.project_manager.save_diagram(diagram_content, file_paths[diagram_type]['output'])

                entities = entity_extraction_service.extract_entities_and_relationships(diagram_content)
                self.project_manager.save_entities_and_relationships(entities, file_paths[diagram_type]['entities'])

            return {"status": "completed", "message": f"Project processing completed: {project_name}"}
        except Exception as e:
            logger.exception(f"Une erreur est survenue lors du traitement du projet {project_name}")
            return {"status": "error", "message": f"Error during processing {project_name}: {str(e)}"}

    async def process_project_diagram(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            project, project_type = self.project_manager.find_project(project_name)
            file_paths = self.project_manager.get_file_paths(project_type, project['name'])

            rag_adapter = RAGAdapter(self.config, self.embedding_service)
            document_adapter = DocumentAdapter(self.config, rag_adapter.openai_chat)
            rag_service = RAGService(rag_adapter)
            document_service = DocumentService(document_adapter)

            content = document_service.load_document(project['path'])
            docs = document_service.split_text(content)
            summary = document_service.summarize_text_parallel(docs)

            prompt_template = self.project_manager.read_prompt_template(file_paths[diagram_type]['prompt'])
            if not prompt_template:
                return {"status": "error",
                        "message": f"Unable to generate diagram {diagram_type} due to prompt reading error"}

            diagram_content = rag_service.generate_with_fallback(prompt_template, content=summary)
            self.project_manager.save_diagram(diagram_content, file_paths[diagram_type]['output'])

            entity_extraction_adapter = EntityExtractionAdapter(rag_adapter.openai_chat)
            entity_extraction_service = EntityExtractionService(entity_extraction_adapter)

            entities = entity_extraction_service.extract_entities_and_relationships(diagram_content)
            self.project_manager.save_entities_and_relationships(entities, file_paths[diagram_type]['entities'])

            return {"status": "completed",
                    "message": f"Project diagram processing completed: {project_name}, {diagram_type}"}
        except Exception as e:
            logger.exception(f"Error during project diagram processing: {str(e)}")
            return {"status": "error", "message": f"Error during processing {project_name}, {diagram_type}: {str(e)}"}

    async def extract_json(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            project, project_type = self.project_manager.find_project(project_name)
            file_paths = self.project_manager.get_file_paths(project_type, project['name'])

            with open(file_paths[diagram_type]['output'], 'r', encoding='utf-8') as f:
                diagram_content = f.read()

            rag_adapter = RAGAdapter(self.config, self.embedding_service)
            entity_extraction_adapter = EntityExtractionAdapter(rag_adapter.openai_chat)
            entity_extraction_service = EntityExtractionService(entity_extraction_adapter)

            entities = entity_extraction_service.extract_entities_and_relationships(diagram_content)
            self.project_manager.save_entities_and_relationships(entities, file_paths[diagram_type]['entities'])

            return {"status": "completed", "message": f"JSON extraction completed: {project_name}, {diagram_type}"}
        except Exception as e:
            logger.exception(f"Error during JSON extraction: {str(e)}")
            return {"status": "error",
                    "message": f"Error during JSON extraction {project_name}, {diagram_type}: {str(e)}"}