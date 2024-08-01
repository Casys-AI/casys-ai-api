import logging
from typing import List, Dict, Any, Union
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain

logger = logging.getLogger("uvicorn.error")


class DocumentAdapter:
    def __init__(self, config: Dict[str, Any], openai_chat: Any):
        self.config = config
        self.openai_chat = openai_chat
        self._validate_config()
        self.text_splitter = self._create_text_splitter()

    def _validate_config(self) -> None:
        required_keys = ["chunk_size", "chunk_overlap"]
        for key in required_keys:
            if key not in self.config.get("text_splitter", {}):
                raise ValueError(f"Configuration manquante : {key}")

    def _create_text_splitter(self) -> RecursiveCharacterTextSplitter:
        return RecursiveCharacterTextSplitter(
            chunk_size=self.config["text_splitter"]["chunk_size"],
            chunk_overlap=self.config["text_splitter"]["chunk_overlap"],
            length_function=len,
            separators=self.config["text_splitter"].get("separators", ["\n\n", "\n", " ", ""])
        )

    def load_document(self, file_path: str) -> str:
        logger.info(f"Début du chargement du document : {file_path}")
        try:
            if file_path.endswith(".pdf"):
                content = self._load_pdf(file_path)
            elif file_path.endswith(".docx"):
                content = self._load_docx(file_path)
            else:
                raise ValueError(f"Format de fichier non supporté : {file_path}")
            logger.info(f"Document chargé avec succès : {file_path}")
            return content
        except Exception as e:
            logger.error(f"Erreur lors du chargement du document {file_path}: {str(e)}")
            raise

    @staticmethod
    def _load_pdf(file_path: str) -> str:
        with open(file_path, "rb") as file:
            pdf_reader = PdfReader(file)
            return "\n".join(page.extract_text() for page in pdf_reader.pages)

    @staticmethod
    def _load_docx(file_path: str) -> str:
        docx_doc = DocxDocument(file_path)
        return "\n".join(para.text for para in docx_doc.paragraphs)

    def split_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[Document]:
        logger.info("Début de la division du texte")
        try:
            chunk_size = chunk_size or self.config["text_splitter"]["chunk_size"]
            chunk_overlap = chunk_overlap or self.config["text_splitter"]["chunk_overlap"]

            chunks = self.text_splitter.split_text(text)
            logger.info(f"Texte divisé en {len(chunks)} morceaux")
            return [Document(page_content=chunk) for chunk in chunks]
        except Exception as e:
            logger.error(f"Erreur lors de la division du texte: {str(e)}")
            raise

    def process_document(self, doc: Union[Document, List[Document]]) -> Dict[str, str]:
        logger.info("Début du traitement du document")
        try:
            chain = load_summarize_chain(self.openai_chat, chain_type="stuff")
            result = chain.invoke([doc] if isinstance(doc, Document) else doc)
            logger.info("Document traité avec succès")
            return {"summary": result['output_text'] if isinstance(result, dict) else result}
        except Exception as e:
            logger.error(f"Erreur lors du traitement du document: {str(e)}")
            raise