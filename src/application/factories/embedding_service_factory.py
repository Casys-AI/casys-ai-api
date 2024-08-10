from src.adapters.web.openai_embedding_adapter import OpenAIEmbeddingAdapter


class EmbeddingServiceFactory:
    @staticmethod
    def create_embedding_service(api_key: str):
        return OpenAIEmbeddingAdapter.create(api_key)
