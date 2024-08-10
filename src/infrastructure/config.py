import os
from pathlib import Path
from typing import Dict, Any, List

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class GlobalConfig(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0
    
    # Neo4j
    NEO4J_URI: str = Field(..., env="NEO4J_URI")
    NEO4J_USER: str = Field(..., env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(..., env="NEO4J_PASSWORD")
    
    # Server
    SERVER_HOST: str = Field(..., env="SERVER_HOST")
    SERVER_PORT: int = Field(..., env="SERVER_PORT")
    
    # Celery
    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(..., env="CELERY_RESULT_BACKEND")
    
    # Environment
    ENV: str = Field(default="development", env="ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_yaml_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


class ProjectConfig:
    def __init__(self):
        self.global_config = GlobalConfig()
        self.yaml_config = load_yaml_config()
    
    def get_project_config(self, project_name: str) -> Dict[str, Any]:
        projects = self.yaml_config.get("projects", [])
        for project in projects:
            if project["name"] == project_name:
                return project
        raise ValueError(f"Configuration for project '{project_name}' not found")
    
    def get_diagram_types(self) -> List[str]:
        return self.yaml_config.get("diagram_types", [])
    
    def get_text_splitter_config(self) -> Dict[str, int]:
        return self.yaml_config.get("text_splitter", {})
    
    def get_similarity_config(self) -> Dict[str, float]:
        return self.yaml_config.get("similarity", {})
    
    def get_celery_config(self) -> Dict[str, Any]:
        return self.yaml_config.get("celery", {})
    
    def get_cors_config(self) -> Dict[str, Any]:
        return self.yaml_config.get("cors", {})


# Instance globale de la configuration
config = ProjectConfig()

# Utilisation:
# from src.infrastructure.config import config
#
# # Accès à la configuration globale
# openai_api_key = config.global_config.OPENAI_API_KEY
#
# # Accès à la configuration spécifique d'un projet
# project_config = config.get_project_config("cdc_1")
#
# # Accès aux types de diagrammes
# diagram_types = config.get_diagram_types()
