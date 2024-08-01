from src.domain.models.diagram import Diagram
from dataclasses import dataclass


@dataclass
class Project:
    def __init__(self, name: str, project_type: str, file_path: str):
        self.name = name
        self.project_type = project_type
        self.file_path = file_path
        self.diagrams = []

    def add_diagram(self, diagram: Diagram):
        self.diagrams.append(diagram)