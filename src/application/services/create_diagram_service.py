# src/application/services/create_diagram_service.py
from src.domain.models.diagram import Diagram
from src.domain.ports.diagram_repository_port import DiagramRepositoryPort


class CreateDiagramService:
    def __init__(self, repository: DiagramRepositoryPort):
        self.repository = repository

    def create_diagram(self, name: str, data: dict) -> Diagram:
        diagram = Diagram(name=name, data=data)
        self.repository.save(diagram)
        return diagram
