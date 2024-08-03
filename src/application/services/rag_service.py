# src/application/services/rag_service.py
from src.domain.ports.rag_adapter_protocol import RAGAdapterProtocol
from langchain.prompts import PromptTemplate


class RAGService:
    def __init__(self, rag_adapter: RAGAdapterProtocol):
        self.rag_adapter = rag_adapter
    
    def generate_with_fallback(self, prompt_template: str, content: str) -> str:
        rag_result, rag_success = self.rag_adapter.rag_pipeline(content, prompt_template)
        if rag_success:
            return rag_result
        
        # Fallback mechanism
        return self.fallback_generation(prompt_template, content)
    
    def fallback_generation(self, prompt_template: str, content: str) -> str:
        # This method should be implemented in RAGAdapter
        return self.rag_adapter.fallback_generation(prompt_template, content)