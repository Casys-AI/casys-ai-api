# src/adapters/celery/celery_factory.py
from src.adapters.celery.celery_adapter import CeleryAdapter
from src.adapters.celery.celery_config import celery_app


def create_celery_adapter():
    return CeleryAdapter(celery_app)
