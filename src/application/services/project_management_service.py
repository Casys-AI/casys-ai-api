import json
import logging
import os
import yaml
from typing import Dict, Any, List
from contextlib import contextmanager

logger = logging.getLogger("uvicorn.error")


#TODO ici configurer la gestion des fichiers / diagrammes par utilisateurs et séparer de la config globale
class ProjectManagementService:
    def __init__(self, config_path: str):
        self.config_path = config_path
        # Assuming load_config() loads the configuration
        self.config = self.load_config(self.config_path)
        if self.config is None:
            logger.error(f"Failed to load config from {self.config_path}")
        logger.debug(f"Loaded config in ProjectManagementService: {self.config}")
    
    def load_config(self, config_path):
        return self.handle_file(self.config_path)  # use the instance variable self.config_path
    
    @staticmethod
    def handle_file(file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r") as config_file:
                content = yaml.safe_load(config_file)
            return content
        except Exception as e:
            logger.exception(f"Error occurred while loading the configuration file: {str(e)}")
            raise
    
    # @contextmanager
    # def log_project_processing(self, project_name: str):
    #     logger.info(f"Début du traitement du projet : {project_name}")
    #     try:
    #         yield
    #     except Exception as e:
    #         logger.exception(f"Erreur lors du traitement du projet {project_name}")
    #     finally:
    #         logger.info(f"Fin du traitement du projet : {project_name}")
    
    def find_project(self, project_name: str) -> Dict[str, Any]:
        for project in self.config['projects']:
            if project['name'] == project_name:
                return project
        raise ValueError(f"Project not found: {project_name}")
    
    def get_project_file_paths(self, project_name: str) -> Dict[str, Any]:
        project = self.find_project(project_name)
        return {
            'input': project['path'],
            'prompts': {
                diagram_type: project['file_templates']['prompt'].format(project_name=project_name,
                                                                         diagram_type=diagram_type)
                for diagram_type in self.get_diagram_types()
            },
            'outputs': {
                diagram_type: project['file_templates']['output'].format(project_name=project_name,
                                                                         diagram_type=diagram_type)
                for diagram_type in self.get_diagram_types()
            },
            'entities': {
                diagram_type: project['file_templates']['entities'].format(project_name=project_name,
                                                                           diagram_type=diagram_type)
                for diagram_type in self.get_diagram_types()
            }
        }
    
    def get_diagram_types(self) -> List[str]:
        return self.config['diagram_types']
    
    def get_project_input_path(self, project_name: str) -> str:
        return self.get_project_file_paths(project_name)['input']
    
    def get_project_prompt_path(self, project_name: str, diagram_type: str) -> str:
        return self.get_project_file_paths(project_name)['prompts'][diagram_type]
    
    def get_project_output_path(self, project_name: str, diagram_type: str) -> str:
        return self.get_project_file_paths(project_name)['outputs'][diagram_type]
    
    def get_project_entities_path(self, project_name: str, diagram_type: str) -> str:
        return self.get_project_file_paths(project_name)['entities'][diagram_type]
    
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
        self._save_file(file_path, diagram, "Diagramme")
    
    def save_entities_and_relationships(self, data: Dict[str, Any], file_path: str) -> None:
        self._save_file(file_path, json.dumps(data, ensure_ascii=False, indent=2), "Entités et relations")
        logger.debug(
            f"Nombre d'entités : {len(data.get('entities', []))}, Nombre de relations : {len(data.get('relationships', []))}")
    
    def _save_file(self, file_path: str, content: str, file_type: str) -> None:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            logger.info(f"{file_type} sauvegardé : {file_path}")
            logger.debug(f"Contenu du {file_type.lower()} : {content[:100]}...")
        except Exception as e:
            logger.exception(f"Erreur lors de la sauvegarde du {file_type.lower()} {file_path}")
    
    def save_json(self, data: Dict[str, Any], file_path: str) -> None:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON sauvegardé : {file_path}")
        except Exception as e:
            logger.exception(f"Erreur lors de la sauvegarde du JSON {file_path}")
    
    def get_project_type(self, project_name: str) -> str:
        project = self.find_project(project_name)
        return project['type']
    
    def get_project_names(self) -> List[str]:
        return [project['name'] for project in self.config['projects']]
    
    def get_project_names_by_type(self, project_type: str) -> List[str]:
        return [project['name'] for project in self.config['projects'] if project['type'] == project_type]
    
    def get_config(self):
        logger.debug(f"get_config() called. Current config: {self.config}")
        return self.config
