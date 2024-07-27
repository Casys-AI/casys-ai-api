# src/application/services/rag_service.py
from src.domain.ports.rag_port import RAGPort
from langchain.prompts import PromptTemplate


class RAGService:
    def __init__(self, rag_port: RAGPort):
        self.rag_port = rag_port

    def generate_with_fallback(self, prompt_template, content):
        rag_result, rag_success = self.rag_port.rag_pipeline(content, prompt_template)
        if rag_success:
            return rag_result
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | self.rag_port.openai_chat
        result = chain.invoke({"content": content})
        return result.content
