# src/application/services/document_service.py
from src.domain.ports.document_port import DocumentPort
from concurrent.futures import ThreadPoolExecutor
from langchain.docstore.document import Document

from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor


class DocumentService:
    def __init__(self, document_port: DocumentPort):
        self.document_port = document_port

    def load_document(self, file_path: str) -> str:
        return self.document_port.load_document(file_path)

    def split_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[Any]:
        return self.document_port.split_text(text, chunk_size, chunk_overlap)

    def summarize_text_parallel(self, docs: List[Any], max_workers: int = 5) -> str:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            summaries = list(executor.map(self.document_port.process_document, docs))

        processed_summaries = []
        for summary in summaries:
            if isinstance(summary, dict):
                # Extrait le texte du résumé du dictionnaire
                summary_text = summary.get('summary', '')
                if isinstance(summary_text, str):
                    processed_summaries.append(summary_text)
                else:
                    processed_summaries.append(str(summary_text))
            elif isinstance(summary, str):
                processed_summaries.append(summary)
            else:
                processed_summaries.append(str(summary))

        return " ".join(processed_summaries)
