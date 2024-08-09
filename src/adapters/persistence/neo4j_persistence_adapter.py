# src/adapters/persistence/neo4j_persistence_adapter.py
import logging
from typing import Dict, List, Any, Optional

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from src.domain.ports.neo4j_persistence_adapter_protocol import Neo4jPersistenceAdapterProtocol

logger = logging.getLogger("uvicorn.error")


# ajouter des transaction sur les requêtes neo4j,par un rollback
#TODO ne pas avoir la config chargée par project manager ici
class Neo4jPersistenceAdapter(Neo4jPersistenceAdapterProtocol):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.driver: Optional[Driver] = None
        self.connect()
    
    def connect(self) -> None:
        try:
            self.driver = GraphDatabase.driver(
                self.config["neo4j"]["uri"],
                auth=(self.config["neo4j"]["user"], self.config["neo4j"]["password"])
            )
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Neo4j connection established successfully")
        except ServiceUnavailable:
            logger.warning("Neo4j is not available. Some features will be limited.")
            self.driver = None
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            self.driver = None
    
    def ensure_connection(self) -> None:
        if not self.is_connected():
            logger.info("Attempting to reconnect to Neo4j...")
            self.connect()
    
    def is_connected(self) -> bool:
        if not self.driver:
            return False
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False
    
    def get_session(self) -> Optional[Session]:
        self.ensure_connection()
        if self.driver:
            return self.driver.session()
        return None
    
    def rollback(self, project_name: str) -> None:
        session = self.get_session()
        if not session:
            logger.warning("Unable to perform rollback: Neo4j is not connected")
            return
        
        query = """
        MATCH (p:Project {name: $project_name})
        DETACH DELETE p
        """
        try:
            session.run(query, project_name=project_name)
            logger.info(f"Rollback completed for project {project_name}")
        except Neo4jError as e:
            logger.error(f"Error during rollback for project {project_name}: {str(e)}")
        finally:
            session.close()
    
    def ensure_vector_index(self) -> None:
        session = self.get_session()
        if not session:
            logger.warning("Unable to create vector index: Neo4j is not connected")
            return
        
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
            logger.info("Vector index 'entity_embeddings' created successfully.")
        except Neo4jError as e:
            if "An equivalent index already exists" in str(e):
                logger.info("Vector index already exists.")
            else:
                logger.error(f"Error creating vector index: {e}")
        finally:
            session.close()


    def create_or_update_entities_and_keywords(self, project_name: str, diagram_type: str, entities: List[Dict[str, Any]]):
        if not self.driver:
            logger.warning("Neo4j driver is not connected. Unable to create or update entities and keywords.")
            return
        
        query = """
        MERGE (p:Project {name: $project_name})
        MERGE (d:Diagram {type: $diagram_type})
        MERGE (p)-[:HAS_DIAGRAM]->(d)
        WITH p, d
        UNWIND $entities AS entity
        MERGE (e:Entity {id: $project_name + '_' + $diagram_type + '_' + entity.id})
        SET e += entity,
            e.project_name = $project_name,
            e.diagram_type = $diagram_type
        MERGE (d)-[:CONTAINS_ENTITY]->(e)
        WITH e, entity
        UNWIND coalesce(entity.keywords, []) AS keyword
        MERGE (k:Keyword {name: keyword})
        MERGE (e)-[:HAS_KEYWORD]->(k)
        """
        
        with self.driver.session() as session:
            result = session.run(query, project_name=project_name, diagram_type=diagram_type, entities=entities)
        logger.info(f"Entities and keywords created/updated: {result.consume().counters}")

    
    def create_or_update_project(self, project_name: str, project_type: str):
        query = """
        MERGE (p:Project {name: $project_name})
        SET p.type = $project_type
        RETURN p
        """
        with self.driver.session() as session:
            session.run(query, project_name=project_name, project_type=project_type)
    
    def create_or_update_diagram(self, project_name: str, diagram_type: str):
        query = """
            MATCH (p:Project {name: $project_name})
            MERGE (d:Diagram {id: $diagram_id})
            SET d.type = $diagram_type, d.project_name = $project_name
            MERGE (p)-[:HAS_DIAGRAM]->(d)
            RETURN d
            """
        diagram_id = f"{project_name}_{diagram_type}"
        with self.driver.session() as session:
            session.run(query, project_name=project_name, diagram_id=diagram_id, diagram_type=diagram_type)
    
    def update_embeddings(self, project_name: str, diagram_type: str, embeddings: Dict[str, List[float]]):
        if not self.driver:
            logger.warning("Neo4j driver is not connected. Unable to update embeddings.")
            return
        query = """
        MATCH (p:Project {name: $project_name})-[:HAS_DIAGRAM]->(d:Diagram {type: $diagram_type})-[:CONTAINS_ENTITY]->(e:Entity)
        WHERE e.id IN $embedding_ids
        SET e.embedding = $embeddings[e.id]
        """
        with self.driver.session() as session:
            result = session.run(query,
                                 project_name=project_name,
                                 diagram_type=diagram_type,
                                 embedding_ids=list(embeddings.keys()),
                                 embeddings=embeddings)
        logger.info(f"Embeddings updated: {result.consume().counters}")
    
    def create_relationships(self, project_name: str, diagram_type: str, relationships: List[Dict[str, Any]]):
        if not self.driver:
            logger.warning("Neo4j driver is not connected. Unable to create relationships.")
            return
        with self.driver.session() as session:
            for rel in relationships:
                query = """
                MATCH (e1:Entity {name: $source, project_name: $project_name, diagram_type: $diagram_type})
                MATCH (e2:Entity {name: $target, project_name: $project_name, diagram_type: $diagram_type})
                MERGE (e1)-[r:`%s`]->(e2)
                """ % rel['type'].upper()
                result = session.run(query,
                                     project_name=project_name,
                                     diagram_type=diagram_type,
                                     source=rel['source'],
                                     target=rel['target'])
                logger.info(f"Relationship created: {result.consume().counters}")
    
    def update_similarity_relationships(self, similarities: List[Dict[str, Any]]):
        if not self.driver:
            logger.warning("Neo4j driver is not connected. Unable to update similarity relationships.")
            return
        query = """
        UNWIND $similarities AS sim
        MATCH (e1:Entity {id: sim.id1})
        MATCH (e2:Entity {id: sim.id2})
        MERGE (e1)-[r:SIMILAR_TO]->(e2)
        SET r.combined_similarity = sim.combined_similarity,
            r.embedding_similarity = sim.embedding_similarity,
            r.jaccard_similarity = sim.jaccard_similarity
        """
        with self.driver.session() as session:
            result = session.run(query, similarities=similarities)
        logger.info(f"Similarity relationships updated: {result.consume().counters}")
    
    def close_neo4j(self) -> None:
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def get_entities_for_similarity(self, project_name: str = None) -> List[Dict[str, Any]]:
        query = """
        MATCH (p:Project)-[:HAS_DIAGRAM]->(d:Diagram)-[:CONTAINS_ENTITY]->(e:Entity)
        WHERE e.embedding IS NOT NULL
        AND (($project_name IS NULL) OR (p.name = $project_name))
        OPTIONAL MATCH (e)-[:HAS_KEYWORD]->(k:Keyword)
        RETURN e.id AS id, e.name AS name, e.embedding AS embedding,
               collect(DISTINCT k.name) AS keywords, d.type AS diagram_type, p.name AS project_name
        """
        with self.driver.session() as session:
            result = session.run(query, project_name=project_name)
            return [dict(record) for record in result]
    