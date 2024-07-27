# src/domain/ports/rag_port.py
class RAGPort:
    def rag_pipeline(self, content, prompt_template):
        raise NotImplementedError("This method should be overridden")
