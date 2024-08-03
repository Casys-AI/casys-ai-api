from typing import Dict

from app_state import app_state  # Assurez-vous d'importer app_state correctement


def get_config():
    return app_state.config


def get_neo4j_adapter():
    return app_state.neo4j_adapter


def get_embedding_adapter():
    return app_state.embedding_adapter


def get_rag_adapter():
    return app_state.rag_adapter


def get_project_manager():
    return app_state.project_manager


def get_project_processing_service():
    return app_state.project_processing_service


def get_neo4j_processing_service():
    return app_state.neo4j_processing_service
