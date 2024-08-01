# src/application/services/document_service.py

from src.domain.ports.document_adapter_protocol import DocumentAdapterProtocol
from concurrent.futures import ThreadPoolExecutor
from typing import List, Any
import logging
import os

logger = logging.getLogger("uvicorn.error")



class DocumentService:
    def __init__(self, document_adapter: DocumentAdapterProtocol):
        self.document_adapter = document_adapter

    def load_document(self, file_path: str) -> str:
        logger.info(f"Tentative de chargement du document : {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"Le fichier n'existe pas : {file_path}")
            raise FileNotFoundError(f"Le fichier n'existe pas : {file_path}")
        return self.document_adapter.load_document(file_path)

    def split_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[Any]:
        """

        :param text:
        :param chunk_size:
        :type chunk_overlap: object
        """
        return self.document_adapter.split_text(text, chunk_size, chunk_overlap)

    def summarize_text_parallel(self, docs: List[Any], max_workers: int = 5) -> str:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            summaries = list(executor.map(self.document_adapter.process_document, docs))

        processed_summaries = []
        for summary in summaries:
            if isinstance(summary, dict):
                summary_text = summary.get('summary', '')
                processed_summaries.append(str(summary_text))
            elif isinstance(summary, str):
                processed_summaries.append(summary)
            else:
                processed_summaries.append(str(summary))

        return " ".join(processed_summaries)