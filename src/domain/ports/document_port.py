# src/domain/ports/document_port.py
from typing import List, Any


class DocumentPort:
    def load_document(self, file_path: str) -> str:
        raise NotImplementedError("This method should be overridden")

    def split_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[Any]:
        raise NotImplementedError("This method should be overridden")

    def process_document(self, doc: Any) -> str:
        raise NotImplementedError("This method should be overridden")