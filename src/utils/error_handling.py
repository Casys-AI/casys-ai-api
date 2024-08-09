# src/utils/error_handling.py
#TODO implémenter
from fastapi import HTTPException

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

def handle_app_error(error: AppError):
    raise HTTPException(status_code=error.status_code, detail=error.message)