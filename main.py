import uvicorn
import os
import logging
from logging.handlers import RotatingFileHandler
from src.adapters.web.api import app

def setup_logging():
    log_level = os.environ.get("LOG_LEVEL", "DEBUG").upper()

    # Configuration du logger principal
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Formatter personnalisé
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Handler pour le fichier avec rotation
    file_handler = RotatingFileHandler("app.log", maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Configuration spécifique pour les tâches en arrière-plan
    background_logger = logging.getLogger('background_tasks')
    background_logger.setLevel(log_level)

    # Ajout d'un handler de console pour les tâches en arrière-plan
    background_console_handler = logging.StreamHandler()
    background_console_handler.setFormatter(formatter)
    background_logger.addHandler(background_console_handler)

    # Handler de fichier spécifique pour les tâches en arrière-plan
    background_file_handler = RotatingFileHandler("background_tasks.log", maxBytes=10 * 1024 * 1024, backupCount=5)
    background_file_handler.setFormatter(formatter)
    background_logger.addHandler(background_file_handler)

    # Configuration spécifique pour uvicorn et fastapi
    for module in ['uvicorn', 'fastapi']:
        mod_logger = logging.getLogger(module)
        mod_logger.handlers = []  # Supprime les handlers existants
        mod_logger.propagate = True  # Propage les logs au logger principal


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting the application...")

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level=os.environ.get("LOG_LEVEL", "info").lower(),
            reload=True
        )
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        raise


if __name__ == "__main__":
    main()