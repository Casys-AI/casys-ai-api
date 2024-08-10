# src/adapters/celery/celery_adapter.py
from typing import Callable, List, Dict, Any
from src.domain.ports.async_task_protocol import AsyncTaskProtocol
from celery import Celery
from celery.result import AsyncResult
import asyncio


class CeleryAdapter(AsyncTaskProtocol):
    def __init__(self, app: Celery):
        self.app = app
    
    def send_task(self, name: str, args: List = None, kwargs: Dict = None) -> Any:
        return self.app.send_task(name, args=args, kwargs=kwargs)
    
    async def monitor_task(self, task_id: str, callback: Callable[[Dict[str, Any]], None]):
        task_result = AsyncResult(task_id, app=self.app)
        while not task_result.ready():
            status = {
                "status": task_result.status,
                "task_id": task_id,
                "result": None
            }
            await callback(status)
            await asyncio.sleep(1)  # Attendre 1 seconde avant la prochaine vérification
        
        final_status = {
            "status": task_result.status,
            "task_id": task_id,
            "result": task_result.result if task_result.successful() else str(task_result.result)
        }
        await callback(final_status)
    
    def create_task(self, func: Callable) -> Callable:
        return self.app.task(func)
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        task_result = AsyncResult(task_id, app=self.app)
        return {
            "status": task_result.status,
            "task_id": task_id,
            "result": task_result.result if task_result.ready() else None
        }
