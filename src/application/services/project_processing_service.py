import logging
from typing import Dict, Any
from src.adapters.web.process_projects import (
    get_file_paths, read_prompt_template, save_diagram,
    save_entities_and_relationships, find_project, log_project_processing
)
from src.adapters.web.rag_adapter import RAGAdapter
from src.adapters.web.document_adapter import DocumentAdapter
from src.adapters.web.entity_extraction_adapter import EntityExtractionAdapter
from src.application.services.rag_service import RAGService
from src.application.services.document_service import DocumentService
from src.application.services.entity_extraction_service import EntityExtractionService
from src.application.services.project_management_service import ProjectManagementService

logger = logging.getLogger(__name__)


class ProjectProcessingService:
    def __init__(self, config_path: str):
        self.project_manager = ProjectManagementService(config_path)

    async def process_project(self, create_diagram_service: Any, project_name: str) -> Dict[str, Any]:
        with self.project_manager.log_project_processing(project_name):
            try:
                project, project_type = self.project_manager.find_project(project_name)
                file_paths = self.project_manager.get_file_paths(project_type, project['name'])

                rag_adapter = RAGAdapter(config)
                document_adapter = DocumentAdapter(config, rag_adapter.openai_chat)
                entity_extraction_adapter = EntityExtractionAdapter(rag_adapter.openai_chat)

                rag_service = RAGService(rag_adapter)
                document_service = DocumentService(document_adapter)
                entity_extraction_service = EntityExtractionService(entity_extraction_adapter)

                # file_paths = get_file_paths(config, project_type, project['name'])
                content = document_service.load_document(project['path'])
                docs = document_service.split_text(content)
                summary = document_service.summarize_text_parallel(docs)

                for diagram_type in self.project_manager.get_config()['diagram_types']:
                    prompt_template = self.project_manager.read_prompt_template(file_paths[diagram_type]['prompt'])
                    if not prompt_template:
                        logger.error(
                            f"Impossible de générer le diagramme {diagram_type} en raison d'une erreur de lecture du prompt")
                        continue

                    diagram_content = rag_service.generate_with_fallback(prompt_template, content=summary)
                    save_diagram(diagram_content, file_paths[diagram_type]['output'])

                    self.project_manager.save_diagram(diagram_content, file_paths[diagram_type]['output'])
                    self.project_manager.save_entities_and_relationships(entities, file_paths[diagram_type]['entities'])

                return {"status": "completed", "message": f"Project processing completed: {project_name}"}

                except Exception as e:
                    logger.exception(f"Une erreur est survenue lors du traitement du projet {project_name}")
                    return {"status": "error", "message": f"Error during processing {project_name}: {str(e)}"}

    @staticmethod
    async def process_project_diagram(config: Dict[str, Any], create_diagram_service: Any, project_name: str,
                                      diagram_type: str) -> Dict[str, Any]:
        try:
            project, project_type = find_project(config, project_name)
            file_paths = get_file_paths(config, project_type, project['name'])

            rag_adapter = RAGAdapter(config)
            document_adapter = DocumentAdapter(config, rag_adapter.openai_chat)
            rag_service = RAGService(rag_adapter)
            document_service = DocumentService(document_adapter)

            content = document_service.load_document(project['path'])
            docs = document_service.split_text(content)
            summary = document_service.summarize_text_parallel(docs)

            prompt_template = read_prompt_template(file_paths[diagram_type]['prompt'])
            if not prompt_template:
                return {"status": "error",
                        "message": f"Unable to generate diagram {diagram_type} due to prompt reading error"}

            diagram_content = rag_service.generate_with_fallback(prompt_template, content=summary)
            save_diagram(diagram_content, file_paths[diagram_type]['output'])

            entity_extraction_adapter = EntityExtractionAdapter(rag_adapter.openai_chat)
            entity_extraction_service = EntityExtractionService(entity_extraction_adapter)

            entities = entity_extraction_service.extract_entities_and_relationships(diagram_content)
            save_entities_and_relationships(entities, file_paths[diagram_type]['entities'])

            return {"status": "completed",
                    "message": f"Project diagram processing completed: {project_name}, {diagram_type}"}
        except Exception as e:
            logger.exception(f"Error during project diagram processing: {str(e)}")
            return {"status": "error", "message": f"Error during processing {project_name}, {diagram_type}: {str(e)}"}

    @staticmethod
    async def extract_json(config: Dict[str, Any], create_diagram_service: Any, project_name: str, diagram_type: str) -> \
    Dict[str, Any]:
        try:
            project, project_type = find_project(config, project_name)
            file_paths = get_file_paths(config, project_type, project['name'])

            with open(file_paths[diagram_type]['output'], 'r', encoding='utf-8') as f:
                diagram_content = f.read()

            rag_adapter = RAGAdapter(config)
            entity_extraction_adapter = EntityExtractionAdapter(rag_adapter.openai_chat)
            entity_extraction_service = EntityExtractionService(entity_extraction_adapter)

            entities = entity_extraction_service.extract_entities_and_relationships(diagram_content)
            save_entities_and_relationships(entities, file_paths[diagram_type]['entities'])

            return {"status": "completed", "message": f"JSON extraction completed: {project_name}, {diagram_type}"}
        except Exception as e:
            logger.exception(f"Error during JSON extraction: {str(e)}")
            return {"status": "error",
                    "message": f"Error during JSON extraction {project_name}, {diagram_type}: {str(e)}"}