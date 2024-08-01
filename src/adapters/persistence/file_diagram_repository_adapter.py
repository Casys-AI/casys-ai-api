# src/adapters/persistence/file_diagram_repository_adapter.py
import json
import os
from src.domain.models.diagram import Diagram


class FileDiagramRepositoryAdapter:
    def __init__(self, directory: str):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def save(self, diagram: Diagram):
        file_path = os.path.join(self.directory, f"{diagram.name}.json")
        with open(file_path, 'w') as file:
            json.dump(diagram.data, file)
