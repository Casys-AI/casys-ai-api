# src/adapters/persistence/neo4j_persistence_adapter.py
import logging
from typing import Dict, List, Any
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import Neo4jError

logger = logging.getLogger("uvicorn.error")


class Neo4jPersistenceAdapter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.driver: Driver = self._connect()

    def _connect(self) -> Driver:
        try:
            driver = GraphDatabase.driver(
                self.config["neo4j"]["uri"],
                auth=(self.config["neo4j"]["user"], self.config["neo4j"]["password"])
            )
            with driver.session() as session:
                session.run("RETURN 1")
            logger.info("Neo4j connection established successfully")
            return driver
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise

    def _check_connection(self):
        if not self.is_connected():
            logger.warning("Neo4j connection lost. Attempting to reconnect...")
            self._connect()

    def ensure_vector_index(self):
        self._check_connection()
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
                logger.info("Vector index 'entity_embeddings' created successfully.")
            except Neo4jError as e:
                if "An equivalent index already exists" in str(e):
                    logger.info("Vector index already exists.")
                else:
                    logger.error(f"Error creating vector index: {e}")
                    raise

    def batch_create_or_update_entities(self, project_name: str, diagram_type: str, entities: List[Dict[str, Any]]):
        query = """
            MATCH (p:Project {name: $project_name})
            MATCH (d:Diagram {id: $diagram_id})
            UNWIND $entities AS entity
            MERGE (e:Entity {id: $project_name + '_' + entity.id})
            SET e += entity, e.project_name = $project_name, e.diagram_type = $diagram_type
            MERGE (d)-[:CONTAINS_ENTITY]->(e)
            WITH e, entity
            UNWIND coalesce(entity.keywords, []) AS keyword
            MERGE (k:Keyword {name: keyword + '_' + $project_name})
            SET k.project_name = $project_name
            MERGE (e)-[:HAS_KEYWORD]->(k)
            """
        diagram_id = f"{project_name}_{diagram_type}"
        with self.driver.session() as session:
            session.run(query, project_name=project_name, diagram_id=diagram_id, diagram_type=diagram_type, entities=entities)

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
        query = """
        MATCH (p:Project {name: $project_name})-[:HAS_DIAGRAM]->(d:Diagram {type: $diagram_type})-[:CONTAINS_ENTITY]->(e:Entity)
        WHERE e.id IN $embedding_ids
        SET e.embedding = $embeddings[e.id]
        """
        with self.driver.session() as session:
            session.run(query,
                        project_name=project_name,
                        diagram_type=diagram_type,
                        embedding_ids=list(embeddings.keys()),
                        embeddings=embeddings)

    def update_similarity_relationships(self, similarities: List[Dict[str, Any]]):
        query = """
        UNWIND $similarities AS sim
        MATCH (e1:Entity {id: sim.id1})
        MATCH (e2:Entity {id: sim.id2})
        MERGE (e1)-[r:SIMILAR_TO]->(e2)
        SET r.combined_similarity = sim.combined_similarity,
            r.embedding_similarity = sim.embedding_similarity,
            r.keyword_similarity = sim.keyword_similarity
        """
        with self.driver.session() as session:
            session.run(query, similarities=similarities)

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

    def rollback(self, project_name: str):
        query = """
        MATCH (p:Project {name: $project_name})
        DETACH DELETE p
        """
        with self.driver.session() as session:
            session.run(query, project_name=project_name)
        logger.info(f"Rollback completed for project {project_name}")

    def close(self):
        if self.driver:
            self.driver.close()

    def is_connected(self) -> bool:
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            logger.error(f"Error verifying Neo4j connection: {e}")
            return False

    def _format_similarity_result(self, record):
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

    def check_and_fix_embeddings(self, project_name: str, diagram_type: str):
        query_check = """
        MATCH (p:Project {name: $project_name})-[:HAS_DIAGRAM]->(d:Diagram {type: $diagram_type})-[:CONTAINS_ENTITY]->(e:Entity)
        WHERE e.embedding IS NOT NULL
        RETURN e.id AS id, e.embedding AS embedding
        """
        query_fix = """
        MATCH (e:Entity {id: $id})
        SET e.embedding = $embedding
        """
        try:
            with self.driver.session() as session:
                result = session.run(query_check, project_name=project_name, diagram_type=diagram_type)
                for record in result:
                    entity_id = record['id']
                    embedding = record['embedding']
                    if isinstance(embedding, str):
                        # Si l'embedding est une chaîne, convertissez-le en liste de nombres
                        try:
                            embedding_list = [float(x) for x in embedding.strip('[]').split(',')]
                            session.run(query_fix, id=entity_id, embedding=embedding_list)
                            logger.info(f"Fixed embedding format for entity {entity_id}")
                        except ValueError:
                            logger.error(f"Unable to convert embedding to list of floats for entity {entity_id}")
                    elif not isinstance(embedding, list) or not all(isinstance(x, (int, float)) for x in embedding):
                        logger.warning(f"Invalid embedding format for entity {entity_id}, setting to empty list")
                        session.run(query_fix, id=entity_id, embedding=[])
                    else:
                        logger.debug(f"Embedding for entity {entity_id} is in the correct format")
                logger.info("Finished checking and fixing embeddings")
        except Neo4jError as e:
            logger.error(f"Neo4j error in check_and_fix_embeddings: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in check_and_fix_embeddings: {str(e)}")
            raise

    def check_and_fix_keywords(self, project_name: str, diagram_type: str):
        query_check = """
        MATCH (p:Project {name: $project_name})-[:HAS_DIAGRAM]->(d:Diagram {type: $diagram_type})-[:CONTAINS_ENTITY]->(e:Entity)
        WHERE e.keywords IS NOT NULL
        RETURN e.id AS id, e.keywords AS keywords
        """
        query_fix = """
        MATCH (e:Entity {id: $id})
        SET e.keywords = $keywords
        """
        try:
            with self.driver.session() as session:
                result = session.run(query_check, project_name=project_name, diagram_type=diagram_type)
                for record in result:
                    entity_id = record['id']
                    keywords = record['keywords']

                    if isinstance(keywords, str):
                        keywords_list = [k.strip() for k in keywords.split(',') if k.strip()]
                        session.run(query_fix, id=entity_id, keywords=keywords_list)
                        logger.info(f"Fixed keywords format for entity {entity_id}: converted string to list")
                    elif not isinstance(keywords, list):
                        session.run(query_fix, id=entity_id, keywords=[])
                        logger.warning(f"Invalid keywords format for entity {entity_id}, set to empty list")
                    else:
                        logger.debug(f"Keywords for entity {entity_id} are already in the correct format")

                logger.info("Finished checking and fixing keywords")
        except Neo4jError as e:
            logger.error(f"Neo4j error in check_and_fix_keywords: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in check_and_fix_keywords: {str(e)}")
            raise