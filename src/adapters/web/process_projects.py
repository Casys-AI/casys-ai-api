import json
import logging
import os
from contextlib import contextmanager
from typing import Dict, Any

import yaml

from src.adapters.web.document_adapter import DocumentAdapter
from src.adapters.web.entity_extraction_adapter import EntityExtractionAdapter
from src.adapters.web.rag_adapter import RAGAdapter
from src.application.services.create_diagram_service import CreateDiagramService
from src.application.services.document_service import DocumentService
from src.application.services.entity_extraction_service import EntityExtractionService
from src.application.services.rag_service import RAGService

logger = logging.getLogger("uvicorn.error")


@contextmanager
def log_project_processing(project_name: str):
    logger.info(f"Début du traitement du projet : {project_name}")
    try:
        yield
    except Exception as e:
        logger.exception(f"Erreur lors du traitement du projet {project_name}")
    finally:
        logger.info(f"Fin du traitement du projet : {project_name}")


def get_file_paths(config: Dict[str, Any], project_type: str, project_name: str) -> Dict[str, Dict[str, str]]:
    template = config['file_templates'][project_type]
    return {
        diagram_type: {
            'prompt': template['prompt'].format(cdc_name=project_name, part_name=project_name,
                                                diagram_type=diagram_type),
            'output': template['output'].format(cdc_name=project_name, part_name=project_name,
                                                diagram_type=diagram_type),
            'entities': template['entities'].format(cdc_name=project_name, part_name=project_name,
                                                    diagram_type=diagram_type)
        } for diagram_type in config['diagram_types']
    }


def check_file_paths(config: Dict[str, Any]) -> None:
    for project_type in ['cdc', 'part']:
        for diagram_type in config['diagram_types']:
            prompt_path = config['file_templates'][project_type]['prompt'].format(
                cdc_name='cdc_1', part_name='crushing_mill', diagram_type=diagram_type
            )
            if not os.path.exists(prompt_path):
                logger.error(f"Le fichier de prompt n'existe pas : {prompt_path}")


def check_project_paths(config: Dict[str, Any]) -> None:
    for project_type in ['cdcs', 'parts']:
        for project in config['projects'][project_type]:
            if not os.path.exists(project['path']):
                logger.error(f"Le fichier du projet n'existe pas : {project['path']}")


def load_config(config_path: str) -> Dict[str, Any]:
    try:
        with open(config_path, "r") as config_file:
            config = yaml.safe_load(config_file)
        check_file_paths(config)
        check_project_paths(config)
        return config
    except Exception as e:
        logger.exception(f"Erreur lors du chargement de la configuration : {str(e)}")
        raise


def process_single_project(config: Dict[str, Any], create_diagram_service: CreateDiagramService,
                           project_name: str) -> None:
    logger.info(f"Traitement du projet: {project_name}")
    try:
        project, project_type = find_project(config, project_name)

        rag_adapter = RAGAdapter(config)
        document_adapter = DocumentAdapter(config, rag_adapter.openai_chat)
        entity_extraction_adapter = EntityExtractionAdapter(rag_adapter.openai_chat)

        rag_service = RAGService(rag_adapter)
        document_service = DocumentService(document_adapter)
        entity_extraction_service = EntityExtractionService(entity_extraction_adapter)

        process_project(config, project_type, project, rag_service, document_service,
                        entity_extraction_service, create_diagram_service)

        logger.info(f"Traitement terminé pour le projet: {project_name}")
    except Exception as e:
        logger.exception(f"Une erreur est survenue lors du traitement du projet {project_name}")
        raise


def read_prompt_template(prompt_path: str) -> str:
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.debug(f"Contenu du prompt lu : {content[:100]}...")
            return content
    except FileNotFoundError:
        logger.error(f"Le fichier de prompt n'a pas été trouvé : {prompt_path}")
    except Exception as e:
        logger.exception(f"Erreur lors de la lecture du fichier de prompt {prompt_path}")
    return ""


def save_diagram(diagram: str, file_path: str) -> None:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(diagram)
        logger.info(f"Diagramme sauvegardé : {file_path}")
        logger.debug(f"Contenu du diagramme : {diagram[:100]}...")
    except Exception as e:
        logger.exception(f"Erreur lors de la sauvegarde du diagramme {file_path}")


def save_entities_and_relationships(data: Dict[str, Any], file_path: str) -> None:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        logger.info(f"Entités et relations sauvegardées : {file_path}")
        logger.debug(
            f"Nombre d'entités : {len(data.get('entities', []))}, Nombre de relations : {len(data.get('relationships', []))}")
    except Exception as e:
        logger.exception(f"Erreur lors de la sauvegarde des entités et relations {file_path}")


def find_project(config: Dict[str, Any], project_name: str) -> Dict[str, Any]:
    for project_type in ['cdcs', 'parts']:
        for project in config['projects'][project_type]:
            if project['name'] == project_name:
                return project, project_type[:-1]
    raise ValueError(f"Project not found: {project_name}")


def process_single_project_diagram(config: Dict[str, Any], create_diagram_service: CreateDiagramService,
                                   project_name: str, diagram_type: str, extract_json_only: bool = False) -> None:
    logger.info(f"Traitement du projet: {project_name}, diagramme: {diagram_type}")
    try:
        project, project_type = find_project(config, project_name)
        file_paths = get_file_paths(config, project_type, project['name'])

        rag_adapter = RAGAdapter(config)

        if not extract_json_only:
            document_adapter = DocumentAdapter(config, rag_adapter.openai_chat)
            rag_service = RAGService(rag_adapter)
            document_service = DocumentService(document_adapter)

            content = document_service.load_document(project['path'])
            docs = document_service.split_text(content)
            summary = document_service.summarize_text_parallel(docs)

            logger.info(f"Génération du diagramme {diagram_type} pour le projet {project['name']}")
            prompt_template = read_prompt_template(file_paths[diagram_type]['prompt'])
            if not prompt_template:
                logger.error(
                    f"Impossible de générer le diagramme {diagram_type} en raison d'une erreur de lecture du prompt")
                return

            diagram_content = rag_service.generate_with_fallback(prompt_template, content=summary)
            save_diagram(diagram_content, file_paths[diagram_type]['output'])
        else:
            with open(file_paths[diagram_type]['output'], 'r', encoding='utf-8') as f:
                diagram_content = f.read()

        entity_extraction_adapter = EntityExtractionAdapter(rag_adapter.openai_chat)
        entity_extraction_service = EntityExtractionService(entity_extraction_adapter)

        entities = entity_extraction_service.extract_entities_and_relationships(diagram_content)
        save_entities_and_relationships(entities, file_paths[diagram_type]['entities'])

        logger.info(f"Traitement terminé pour le projet: {project_name}, diagramme: {diagram_type}")
    except Exception as e:
        logger.exception(
            f"Une erreur est survenue lors du traitement du projet {project_name}, diagramme {diagram_type}")
        raise


def process_project(config: Dict[str, Any], project_type: str, project: Dict[str, Any],
                    rag_service: RAGService, document_service: DocumentService,
                    entity_extraction_service: EntityExtractionService,
                    create_diagram_service: CreateDiagramService) -> None:
    with log_project_processing(project['name']):
        try:
            file_paths = get_file_paths(config, project_type, project['name'])
            logger.debug(f"Chemins des fichiers pour le projet : {file_paths}")

            content = document_service.load_document(project['path'])
            logger.debug(f"Contenu du document chargé : {content[:100]}...")

            docs = document_service.split_text(content)
            summary = document_service.summarize_text_parallel(docs)
            logger.debug(f"Résumé du document : {summary[:100]}...")

            for diagram_type in config['diagram_types']:
                logger.info(f"Génération du diagramme {diagram_type} pour le projet {project['name']}")
                prompt_template = read_prompt_template(file_paths[diagram_type]['prompt'])
                if not prompt_template:
                    logger.error(
                        f"Impossible de générer le diagramme {diagram_type} en raison d'une erreur de lecture du prompt")
                    continue

                diagram_content = rag_service.generate_with_fallback(prompt_template, content=summary)
                logger.debug(f"Contenu du diagramme généré : {diagram_content[:100]}...")

                save_diagram(diagram_content, file_paths[diagram_type]['output'])

                entities = entity_extraction_service.extract_entities_and_relationships(diagram_content)
                save_entities_and_relationships(entities, file_paths[diagram_type]['entities'])

            logger.info(f"Extraction des entités et relations terminée pour le projet {project['label']}.")
        except Exception as e:
            logger.exception(f"Une erreur est survenue lors du traitement du projet {project['name']}")


def process_projects(config: Dict[str, Any], create_diagram_service: CreateDiagramService) -> None:
    logger.info("Début du traitement des projets")
    try:
        rag_adapter = RAGAdapter(config)
        document_adapter = DocumentAdapter(config, rag_adapter.openai_chat)
        entity_extraction_adapter = EntityExtractionAdapter(rag_adapter.openai_chat)

        rag_service = RAGService(rag_adapter)
        document_service = DocumentService(document_adapter)
        entity_extraction_service = EntityExtractionService(entity_extraction_adapter)

        for project_type in ['cdcs', 'parts']:
            logger.info(f"Traitement des projets de type {project_type}")
            projects = config['projects'][project_type]
            for i, project in enumerate(projects, 1):
                logger.info(f"Traitement du projet {i}/{len(projects)} : {project['name']}")
                process_project(config, project_type[:-1], project, rag_service, document_service,
                                entity_extraction_service, create_diagram_service)
    except Exception as e:
        logger.exception("Une erreur est survenue lors du traitement des projets")
    finally:
        logger.info("Fin du traitement des projets")


# Chargement de la configuration
try:
    config = load_config("config.yaml")
    logger.info("Configuration chargée avec succès.")
except Exception as e:
    logger.error(f"Impossible de charger la configuration : {str(e)}")
    raise
