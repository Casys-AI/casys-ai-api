# src/adapters/web/document_adapter.py
import logging
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from src.domain.ports.document_port import DocumentPort

logger = logging.getLogger(__name__)


def _document_load_pdf(file_path: str) -> str:
    """
    Charge et extrait le texte d'un fichier PDF.

    Args:
        file_path (str): Chemin vers le fichier PDF.

    Returns:
        str: Texte extrait du PDF.
    """
    with open(file_path, "rb") as file:
        pdf_reader = PdfReader(file)
        return "\n".join(page.extract_text() for page in pdf_reader.pages)


def _document_load_docx(file_path: str) -> str:
    """
    Charge et extrait le texte d'un fichier DOCX.

    Args:
        file_path (str): Chemin vers le fichier DOCX.

    Returns:
        str: Texte extrait du DOCX.
    """
    docx_doc = DocxDocument(file_path)
    return "\n".join(para.text for para in docx_doc.paragraphs)


class DocumentAdapter(DocumentPort):
    """
    Adaptateur pour le traitement de documents.
    Implémente les méthodes définies dans DocumentPort.
    """

    def __init__(self, config: Dict[str, Any], openai_chat: Any):
        """
        Initialise l'adaptateur avec la configuration et le chat OpenAI.

        Args:
            config (Dict[str, Any]): Configuration pour le traitement de documents.
            openai_chat (Any): Instance du chat OpenAI pour le traitement.
        """
        self.config = config
        self.openai_chat = openai_chat
        self._validate_config()
        self.text_splitter = self._create_text_splitter()

    def _validate_config(self) -> None:
        """
        Valide la configuration fournie.

        Raises:
            ValueError: Si des clés de configuration requises sont manquantes.
        """
        required_keys = ["chunk_size", "chunk_overlap"]
        for key in required_keys:
            if key not in self.config.get("text_splitter", {}):
                raise ValueError(f"Configuration manquante : {key}")

    def _create_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Crée et configure le diviseur de texte.

        Returns:
            RecursiveCharacterTextSplitter: Instance configurée du diviseur de texte.
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=self.config["text_splitter"]["chunk_size"],
            chunk_overlap=self.config["text_splitter"]["chunk_overlap"],
            length_function=len,
            separators=self.config["text_splitter"].get("separators", ["\n\n", "\n", " ", ""])
        )

    def load_document(self, file_path: str) -> str:
        """
        Charge un document à partir du chemin de fichier spécifié.

        Args:
            file_path (str): Chemin vers le fichier à charger.

        Returns:
            str: Contenu du document.

        Raises:
            ValueError: Si le format de fichier n'est pas supporté.
        """
        logger.info(f"Début du chargement du document : {file_path}")
        try:
            if file_path.endswith(".pdf"):
                content = _document_load_pdf(file_path)
            elif file_path.endswith(".docx"):
                content = _document_load_docx(file_path)
            else:
                raise ValueError(f"Format de fichier non supporté : {file_path}")
            logger.info(f"Document chargé avec succès : {file_path}")
            return content
        except Exception as e:
            logger.error(f"Erreur lors du chargement du document {file_path}: {str(e)}")
            raise

    def split_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[Document]:
        """
        Divise le texte en morceaux plus petits.

        Args:
            text (str): Texte à diviser.
            chunk_size (int, optional): Taille des morceaux.
            chunk_overlap (int, optional): Chevauchement entre les morceaux.

        Returns:
            List[Document]: Liste des morceaux de texte sous forme de Documents.
        """
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

    def process_document(self, doc: Any) -> Dict[str, str]:
        """
        Traite un document en utilisant le modèle de langage.

        Args:
            doc (Any): Document à traiter.

        Returns:
            Dict[str, str]: Résumé du document.
        """
        logger.info("Début du traitement du document")
        try:
            chain = load_summarize_chain(self.openai_chat, chain_type="stuff")
            result = chain.invoke([doc] if isinstance(doc, Document) else doc)
            logger.info("Document traité avec succès")
            return {"summary": result['output_text'] if isinstance(result, dict) else result}
        except Exception as e:
            logger.error(f"Erreur lors du traitement du document: {str(e)}")
            raise
