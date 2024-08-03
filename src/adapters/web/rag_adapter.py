import logging
from typing import Dict, List, Tuple, Optional
import re
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_random_exponential

from src.adapters.web.openai_embedding_adapter import OpenAIEmbeddingAdapter
from src.domain.ports.rag_adapter_protocol import RAGAdapterProtocol
from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter

logger = logging.getLogger("uvicorn.error")


class RAGAdapter(RAGAdapterProtocol):
    def __init__(self, config: Dict, embedding_adapter: OpenAIEmbeddingAdapter, neo4j_adapter: Neo4jPersistenceAdapter):
        self.config = config
        self.embedding_adapter = embedding_adapter
        self.openai_chat = ChatOpenAI(
            model_name=config["openai"]["model"],
            temperature=config["openai"]["temperature"],
            openai_api_key=config["openai"]["api_key"]
        )
        self.neo4j_adapter = neo4j_adapter
    
    def fallback_generation(self, prompt_template: str, content: str) -> str:
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | self.openai_chat
        result = chain.invoke({"content": content})
        return result.content
    
    def hybrid_search_with_fallback(self, query: str, semantic_top_k: int = 5, graph_depth: int = 2) -> List[
        Tuple[str, str]]:
        if not self.neo4j_adapter.is_connected():
            logger.warning("Neo4j n'est pas connecté. Utilisation de la recherche par mot-clé comme solution de repli.")
            return self.keyword_search_fallback(query, semantic_top_k)
        
        try:
            query_embedding = self.embedding_adapter.get_query_embedding(query)
            
            with self.neo4j_adapter.get_session() as session:
                semantic_results = session.run("""
                CALL db.index.vector.queryNodes('entity_embeddings', $k, $embedding)
                YIELD node, score
                RETURN node.name AS name, node.description AS description, score
                """, k=semantic_top_k, embedding=query_embedding).data()
                
                semantic_entity_names = [result['name'] for result in semantic_results]
                graph_results = session.run("""
                MATCH (e:Entity)
                WHERE e.name IN $entity_names
                CALL apoc.path.subgraphNodes(e, {
                    maxLevel: $max_depth,
                    relationshipFilter: '>',
                    labelFilter: '+Entity'
                })
                YIELD node
                RETURN DISTINCT node.name AS name, node.description AS description
                """, entity_names=semantic_entity_names, max_depth=graph_depth).data()
            
            all_results = set([(r['name'], r['description']) for r in semantic_results + graph_results])
            logger.debug(f"Résultats de la recherche hybride : {list(all_results)[:5]}...")
            return list(all_results)
        
        except Exception as e:
            logger.warning(f"Erreur lors de la recherche vectorielle : {str(e)}")
            return self.keyword_search_fallback(query, semantic_top_k)
    
    def keyword_search_fallback(self, query: str, limit: int) -> List[Tuple[str, str]]:
        results = []
        query_keywords = set(re.findall(r'\w+', query.lower()))
        
        with self.neo4j_adapter.get_session() as session:
            entities = session.run("""
            MATCH (e:Entity)
            RETURN e.name AS name, e.description AS description, e.keywords AS keywords
            """).data()
            
            for entity in entities:
                entity_keywords = set(entity.get('keywords', []))
                entity_text = f"{entity['name']} {entity['description']}".lower()
                entity_text_keywords = set(re.findall(r'\w+', entity_text))
                
                keyword_match_score = len(query_keywords.intersection(entity_keywords))
                text_match_score = len(query_keywords.intersection(entity_text_keywords))
                
                total_score = keyword_match_score + text_match_score
                
                if total_score > 0:
                    results.append((total_score, entity['name'], entity['description']))
        
        results.sort(reverse=True, key=lambda x: x[0])
        return [(name, description) for _, name, description in results[:limit]]
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def rag_pipeline(self, content: str, prompt_template: str) -> Tuple[Optional[str], bool]:
        try:
            relevant_entities = self.hybrid_search_with_fallback(content)
            context = "Entités pertinentes trouvées :\n" + "\n".join(
                [f"- {name}: {description}" for name, description in relevant_entities])
            enriched_prompt = f"{context}\n\n{prompt_template}\n\nContenu à analyser :\n{content}"
            prompt = PromptTemplate.from_template(enriched_prompt)
            chain = prompt | self.openai_chat
            result = chain.invoke({"content": content})
            return result.content, True
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec RAG : {str(e)}")
            return None, False
