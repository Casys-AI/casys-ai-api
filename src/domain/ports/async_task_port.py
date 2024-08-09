# src/domain/ports/async_task_port.py
from typing import Protocol, Any, Callable

class AsyncTaskPort(Protocol):
    def send_task(self, name: str, args: list = None, kwargs: dict = None) -> Any:
        ...
    
    async def monitor_task(self, task_id: str, callback: Callable[[dict], None]):
        ...
    
    def create_task(self, func: Callable) -> Callable:
        ...