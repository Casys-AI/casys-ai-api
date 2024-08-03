# src/domain/ports/rag_adapter_protocol.py

from typing import List, Tuple, Optional, Protocol


class RAGAdapterProtocol(Protocol):
    def hybrid_search_with_fallback(self, query: str, semantic_top_k: int , graph_depth: int ) -> List[Tuple[str, str]]:
        ...
    
    def rag_pipeline(self, content: str, prompt_template: str) -> Tuple[Optional[str], bool]:
        ...
    
    def fallback_generation(self, prompt_template: str, content: str) -> str:
        ...