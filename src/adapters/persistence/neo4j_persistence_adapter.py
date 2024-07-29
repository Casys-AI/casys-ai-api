# src/adapters/persistence/neo4j_persistence_adapter.py

import logging
from typing import Dict, List, Any
from neo4j import GraphDatabase
from src.domain.ports.similarity_port import SimilarityPort

logger = logging.getLogger(__name__)

def _neo4j_create_relationships(tx, project_name: str, relationships: List[Dict[str, Any]]):
    query = """
    MATCH (p:Project {name: $project_name})
    WITH p
    UNWIND $relationships AS rel
    MATCH (s:Entity {id: rel.source_id})<-[:CONTAINS_ENTITY]-(:Diagram)<-[:HAS_DIAGRAM]-(p)
    MATCH (t:Entity {id: rel.target_id})<-[:CONTAINS_ENTITY]-(:Diagram)<-[:HAS_DIAGRAM]-(p)
    CALL apoc.merge.relationship(s, rel.type, {}, {}, t)
    YIELD rel AS created_rel
    RETURN count(created_rel)
    """
    tx.run(query, project_name=project_name, relationships=relationships)

def _neo4j_create_or_update_entities(tx, project_name: str, diagram_type: str, entities: List[Dict[str, Any]]):
    query = """
    MERGE (p:Project {name: $project_name})
    WITH p
    UNWIND $entities AS entity
    MERGE (d:Diagram {type: $diagram_type, project: p.name})
    MERGE (e:Entity {id: entity.id})
    SET e += entity
    MERGE (d)-[:CONTAINS_ENTITY]->(e)
    WITH e, entity
    UNWIND entity.keywords AS keyword
    MERGE (k:Keyword {name: keyword})
    MERGE (e)-[:HAS_KEYWORD]->(k)
    """
    tx.run(query, project_name=project_name, diagram_type=diagram_type, entities=entities)

class Neo4jPersistenceAdapter(SimilarityPort):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.driver = GraphDatabase.driver(
            config["neo4j"]["uri"],
            auth=(config["neo4j"]["user"], config["neo4j"]["password"])
        )

    def save(self, project_name: str, diagram_type: str, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]):
        """
        Sauvegarde les entités et les relations dans Neo4j.
        """
        with self.driver.session() as session:
            session.execute_write(_neo4j_create_or_update_entities, project_name, diagram_type, entities)
            session.execute_write(_neo4j_create_relationships, project_name, relationships)

    def ensure_vector_index(self):
        """
        Crée l'index vectoriel si nécessaire.
        """
        with self.driver.session() as session:
            try:
                session.run("""
                CALL db.index.vector.createNodeIndex(
                  'entity_embeddings',
                  'Entity',
                  'embedding',
                  1536,
                  'cosine'
                )
                """)
                logger.info("Index vectoriel 'entity_embeddings' créé avec succès.")
            except Exception as e:
                if "An equivalent index already exists" in str(e):
                    logger.info("L'index vectoriel existe déjà.")
                else:
                    logger.error(f"Erreur lors de la création de l'index vectoriel : {e}")

    def update_embeddings(self, project_name: str, diagram_type: str, embeddings: Dict[str, List[float]]):
        query = """
        MATCH (p:Project {name: $project_name})-[:HAS_DIAGRAM]->(d:Diagram {type: $diagram_type})-[:CONTAINS_ENTITY]->(e:Entity)
        WHERE e.id IN $embedding_ids
        SET e.embedding = $embeddings[e.id]
        """
        with self.driver.session() as session:
            session.run(query, project_name=project_name, diagram_type=diagram_type,
                        embedding_ids=list(embeddings.keys()), embeddings=embeddings)

    def calculate_similarities_with_existing(self, new_entity_ids: List[str]) -> List[Dict[str, Any]]:
        query = """
        MATCH (e1:Entity)
        WHERE e1.id IN $new_entity_ids
        MATCH (e2:Entity)
        WHERE e2.id <> e1.id
        WITH e1, e2, 
             gds.similarity.cosine(e1.embedding, e2.embedding) AS embedding_similarity,
             gds.similarity.jaccard(e1.keywords, e2.keywords) AS keyword_similarity
        WHERE embedding_similarity > $similarity_threshold OR keyword_similarity > $similarity_threshold
        RETURN e1.id AS id1, e2.id AS id2, embedding_similarity, keyword_similarity
        """
        with self.driver.session() as session:
            result = session.run(query, new_entity_ids=new_entity_ids,
                                 similarity_threshold=self.config['similarity']['threshold'])
            return [self._format_similarity_result(record) for record in result]

    def update_similarity_relationships(self, similarities: List[Dict[str, Any]]):
        query = """
        UNWIND $similarities AS sim
        MATCH (e1:Entity {id: sim.id1}), (e2:Entity {id: sim.id2})
        MERGE (e1)-[r:SIMILAR_TO]->(e2)
        SET r.score = sim.combined_similarity,
            r.embedding_similarity = sim.embedding_similarity,
            r.keyword_similarity = sim.keyword_similarity
        """
        with self.driver.session() as session:
            session.run(query, similarities=similarities)

    def get_entities_for_similarity(self, project_name: str, diagram_type: str = None) -> List[Dict[str, Any]]:
        query = """
        MATCH (p:Project {name: $project_name})-[:HAS_DIAGRAM]->(d:Diagram)-[:CONTAINS_ENTITY]->(e:Entity)
        WHERE e.embedding IS NOT NULL
        """
        if diagram_type:
            query += " AND d.type = $diagram_type"
        query += """
        RETURN e.id AS id, e.embedding AS embedding, d.type AS diagramType, 
               [(e)-[:HAS_KEYWORD]->(k) | k.name] AS keywords
        """
        with self.driver.session() as session:
            result = session.run(query, project_name=project_name, diagram_type=diagram_type)
            return [record.data() for record in result]

    def rollback(self, project_name: str):
        query = """
        MATCH (p:Project {name: $project_name})
        DETACH DELETE p
        """
        with self.driver.session() as session:
            session.run(query, project_name=project_name)
        logger.info(f"Rollback completed for project {project_name}")

    def is_connected(self) -> bool:
        """
        Vérifie si la connexion à Neo4j est active.
        """
        try:
            return self.driver.verify_connectivity()
        except Exception as e:
            logger.error(f"Error verifying Neo4j connection: {e}")
            return False

    def close(self):
        """
        Ferme la connexion à Neo4j.
        """
        self.driver.close()

    def _format_similarity_result(self, record):
        """
        Formate le résultat de similarité.
        """
        embedding_weight = self.config['similarity']['embedding_weight']
        keyword_weight = self.config['similarity']['keyword_weight']
        total_weight = embedding_weight + keyword_weight
        return {
            'id1': record['id1'],
            'id2': record['id2'],
            'combined_similarity': (embedding_weight * record['embedding_similarity'] +
                                    keyword_weight * record['keyword_similarity']) / total_weight,
            'embedding_similarity': record['embedding_similarity'],
            'keyword_similarity': record['keyword_similarity']
        }