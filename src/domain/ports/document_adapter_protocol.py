# src/domain/ports/document_adapter_protocol.py
from typing import List, Any, Protocol


class DocumentAdapterProtocol(Protocol):
    """This class represents a protocol for a document adapter.

    The DocumentAdapterProtocol class is an abstract class that defines a set of methods that must be implemented by any concrete class that wants to act as a document adapter. These methods allow loading a document, splitting its text into chunks, and processing the document.

    Methods:
        - load_document(file_path: str) -> str: Loads a document from the specified file path and returns its contents as a string.
        - split_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[Any]: Splits the given text into chunks of specified size with a specified overlap and returns a list of chunks.
        - process_document(doc: Any) -> str: Processes the given document and returns a processed version as a string.

    Note:
        This is an abstract class and should not be instantiated directly. Concrete classes should extend this class and implement the required methods.

    Example:
        class MyDocumentAdapter(DocumentAdapterProtocol):
            def load_document(self, file_path: str) -> str:
                # Implementation goes here

            def split_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[Any]:
                # Implementation goes here

            def process_document(self, doc: Any) -> str:
                # Implementation goes here
    """
    def load_document(self, file_path: str) -> str:
        """
        Load a document from the given file path.

        :param file_path: The path to the document file.
        :return: The content of the loaded document as a string.
        """
        raise NotImplementedError("This method should be overridden")

    def split_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[Any]:
        """
        Split the given text into chunks of specified size, with optional overlap.

        :param text: The text to be split into chunks.
        :type text: str

        :param chunk_size: The size of each chunk. If not specified, the text will be split into individual characters.
        :type chunk_size: int, optional

        :param chunk_overlap: The amount of overlap between consecutive chunks. If not specified, there will be no overlap.
        :type chunk_overlap: int, optional

        :return: A list of chunks generated from the input text.
        :rtype: List[Any]
        """
        raise NotImplementedError("This method should be overridden")

    def process_document(self, doc: Any) -> str:
        """

        :param doc: The document to be processed.
        :return: The result of processing the document.

        """
        raise NotImplementedError("This method should be overridden")
