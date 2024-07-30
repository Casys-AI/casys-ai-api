import json
import logging
import os
import yaml
from typing import Dict, Any, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)


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


class ProjectManagementService:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = load_config(config_path)

    @contextmanager
    def log_project_processing(self, project_name: str):
        logger.info(f"Début du traitement du projet : {project_name}")
        try:
            yield
        except Exception as e:
            logger.exception(f"Erreur lors du traitement du projet {project_name}")
        finally:
            logger.info(f"Fin du traitement du projet : {project_name}")

    def get_file_paths(self, project_type: str, project_name: str) -> Dict[str, Dict[str, str]]:
        template = self.config['file_templates'][project_type]
        return {
            diagram_type: {
                'prompt': template['prompt'].format(cdc_name=project_name, part_name=project_name, diagram_type=diagram_type),
                'output': template['output'].format(cdc_name=project_name, part_name=project_name, diagram_type=diagram_type),
                'entities': template['entities'].format(cdc_name=project_name, part_name=project_name, diagram_type=diagram_type)
            } for diagram_type in self.config['diagram_types']
        }

    def read_prompt_template(self, prompt_path: str) -> str:
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

    def save_diagram(self, diagram: str, file_path: str) -> None:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(diagram)
            logger.info(f"Diagramme sauvegardé : {file_path}")
            logger.debug(f"Contenu du diagramme : {diagram[:100]}...")
        except Exception as e:
            logger.exception(f"Erreur lors de la sauvegarde du diagramme {file_path}")

    def save_entities_and_relationships(self, data: Dict[str, Any], file_path: str) -> None:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            logger.info(f"Entités et relations sauvegardées : {file_path}")
            logger.debug(f"Nombre d'entités : {len(data.get('entities', []))}, Nombre de relations : {len(data.get('relationships', []))}")
        except Exception as e:
            logger.exception(f"Erreur lors de la sauvegarde des entités et relations {file_path}")

    def find_project(self, project_name: str) -> Tuple[Dict[str, Any], str]:
        for project_type in ['cdcs', 'parts']:
            for project in self.config['projects'][project_type]:
                if project['name'] == project_name:
                    return project, project_type[:-1]
        raise ValueError(f"Project not found: {project_name}")

    def get_config(self) -> Dict[str, Any]:
        return self.config