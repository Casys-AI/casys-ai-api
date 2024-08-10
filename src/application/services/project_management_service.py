import json
import logging
import os
from typing import Dict, Any, List
from pathlib import Path

from src.infrastructure.config import config

logger = logging.getLogger("uvicorn.error")


class ProjectManagementService:
    def __init__(self):
        self.config = config
        logger.debug(f"Initialized ProjectManagementService with config: {self.config}")
    
    def find_project(self, project_name: str) -> Dict[str, Any]:
        try:
            return self.config.get_project_config(project_name)
        except ValueError as e:
            logger.error(f"Project not found: {project_name}")
            raise
    
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
        return self.config.get_diagram_types()
    
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
                logger.debug(f"Prompt content read: {content[:100]}...")
                return content
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {prompt_path}")
        except Exception as e:
            logger.exception(f"Error reading prompt file {prompt_path}")
        return ""
    
    def save_diagram(self, diagram: str, file_path: str) -> None:
        self._save_file(file_path, diagram, "Diagram")
    
    def save_entities_and_relationships(self, data: Dict[str, Any], file_path: str) -> None:
        self._save_file(file_path, json.dumps(data, ensure_ascii=False, indent=2), "Entities and relationships")
        logger.debug(
            f"Number of entities: {len(data.get('entities', []))}, Number of relationships: {len(data.get('relationships', []))}")
    
    def _save_file(self, file_path: str, content: str, file_type: str) -> None:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            logger.info(f"{file_type} saved: {file_path}")
            logger.debug(f"{file_type} content: {content[:100]}...")
        except Exception as e:
            logger.exception(f"Error saving {file_type.lower()} {file_path}")
    
    def save_json(self, data: Dict[str, Any], file_path: str) -> None:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON saved: {file_path}")
        except Exception as e:
            logger.exception(f"Error saving JSON {file_path}")
    
    def get_project_type(self, project_name: str) -> str:
        project = self.find_project(project_name)
        return project['type']
    
    def get_project_names(self) -> List[str]:
        return [project['name'] for project in self.config.yaml_config['projects']]
    
    def get_project_names_by_type(self, project_type: str) -> List[str]:
        return [project['name'] for project in self.config.yaml_config['projects'] if project['type'] == project_type]
    
    def get_config(self):
        return self.config
