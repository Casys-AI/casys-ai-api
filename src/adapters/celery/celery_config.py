# src/adapters/celery/celery_config.py
from celery import Celery
from src.utils.config import GLOBAL_CONFIG


def create_celery_app():
    app = Celery('smaas_project',
                 broker=GLOBAL_CONFIG['celery']['broker'],
                 backend=GLOBAL_CONFIG['celery']['backend'],
                 include=GLOBAL_CONFIG['celery']['include'])
    
    app.conf.update(GLOBAL_CONFIG['celery'].get('config', {}))
    
    return app


celery_app = create_celery_app()
