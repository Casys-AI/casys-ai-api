from celery import Celery
from src.infrastructure.config import config


def create_celery_app():
    celery_config = config.get_celery_config()
    app = Celery('smaas_project',
                 broker=config.global_config.CELERY_BROKER_URL,
                 backend=config.global_config.CELERY_RESULT_BACKEND,
                 include=celery_config['include'])
    
    app.conf.update(celery_config.get('config', {}))
    return app


celery_app = create_celery_app()
