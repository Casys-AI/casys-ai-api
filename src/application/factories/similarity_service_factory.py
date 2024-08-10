# src/application/factories/similarity_service_factory.py

from src.application.services.similarity_processing_service import SimilarityService
from src.infrastructure.config import config


class SimilarityServiceFactory:
    @staticmethod
    def create_similarity_service():
        similarity_config = config.get_similarity_config()
        return SimilarityService.create(similarity_config)
