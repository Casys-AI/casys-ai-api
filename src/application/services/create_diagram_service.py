# src/application/services/create_diagram_service.py
from src.domain.models.diagram import Diagram
from src.domain.ports.diagram_repository_adapter_protocol import DiagramRepositoryProtocol


class CreateDiagramService:
    def __init__(self, repository_adapter: DiagramRepositoryProtocol):
        self.repository_adapter = repository_adapter

    def create_diagram(self, name: str, data: dict) -> Diagram:
        diagram = Diagram(name=name, data=data)
        self.repository_adapter.save(diagram)
        return diagram
