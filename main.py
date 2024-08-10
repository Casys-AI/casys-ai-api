# main.py
import uvicorn
import os
import logging
from logging.handlers import RotatingFileHandler
from src.infrastructure.config import config


def setup_logging(config_log_level: str):
    # Configuration of the main logger
    root_logger = logging.getLogger("uvicorn.error")
    root_logger.setLevel(logging.DEBUG)  # Capture all log levels
    
    # Custom formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config_log_level.upper())
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation (all logs)
    file_handler = RotatingFileHandler("app.log", maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Adjust log level for uvicorn.access if necessary
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)


if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL", "debug")
    setup_logging(log_level)
    
    logger = logging.getLogger("uvicorn.error")  # Updated line
    logger.info("Starting the application...")
    
    try:
        uvicorn.run(
            "src.adapters.web.api:app",
            host=config.global_config.SERVER_HOST,
            port=config.global_config.SERVER_PORT,
            log_level=log_level.lower(),
            reload=True
        )
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        raise
