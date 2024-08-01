# src/adapters/persistence/neo4j_persistence_adapter.py
import logging
from typing import Dict, List, Any
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

logger = logging.getLogger("uvicorn.error")


class Neo4jPersistenceAdapter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.driver = None
        self._connect()

    def _connect(self):
        try:
            logger.info(f"Attempting to connect to Neo4j with URI: {self.config['neo4j']['uri']}")
            self.driver = GraphDatabase.driver(
                self.config["neo4j"]["uri"],
                auth=(self.config["neo4j"]["user"], self.config["neo4j"]["password"])
            )
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS num")
                for record in result:
                    logger.info(f"Neo4j connection test successful. Result: {record['num']}")
            logger.info("Neo4j connection established successfully")
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

    def batch_create_or_update_entities(self, entities: List[Dict[str, Any]], project_name: str, diagram_type: str):
        query = """
        MERGE (p:Project {name: $project_name})
        MERGE (d:Diagram {type: $diagram_type})
        MERGE (p)-[:HAS_DIAGRAM]->(d)
        WITH p, d
        UNWIND $entities AS entity
        MERGE (e:Entity {id: entity.id})
        SET e += entity
        MERGE (d)-[:CONTAINS_ENTITY]->(e)
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, project_name=project_name, diagram_type=diagram_type, entities=entities)
                logger.info(
                    f"Created or updated {result.consume().counters.nodes_created} entities for project {project_name}, diagram type {diagram_type}")
        except Neo4jError as e:
            logger.error(f"Neo4j error in batch_create_or_update_entities: {str(e)}")
            raise

    @staticmethod
    def _neo4j_create_or_update_entities(tx, entities: List[Dict[str, Any]], project_name: str, diagram_type: str):
        query = """
        MERGE (p:Project {name: $project_name})
        MERGE (d:Diagram {type: $diagram_type, project: p.name})
        MERGE (p)-[:HAS_DIAGRAM]->(d)
        WITH p, d
        UNWIND $entities AS entity
        MERGE (e:Entity {id: entity.id})
        SET e += entity
        MERGE (d)-[:CONTAINS_ENTITY]->(e)
        WITH e, entity
        UNWIND coalesce(entity.keywords, []) AS keyword
        MERGE (k:Keyword {name: keyword})
        MERGE (e)-[:HAS_KEYWORD]->(k)
        """
        return tx.run(query, project_name=project_name, diagram_type=diagram_type, entities=entities)

    def batch_create_relationships(self, relationships: List[Dict[str, Any]], project_name: str):
        self._check_connection()
        try:
            with self.driver.session() as session:
                result = session.execute_write(self._neo4j_create_relationships, relationships, project_name)
            logger.info(f"Successfully created {len(relationships)} relationships for project {project_name}")
            return result
        except Neo4jError as e:
            logger.error(f"Neo4j error in batch_create_relationships: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in batch_create_relationships: {str(e)}")
            raise

    @staticmethod
    def _neo4j_create_relationships(tx, relationships: List[Dict[str, Any]], project_name: str):
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
        return tx.run(query, project_name=project_name, relationships=relationships)

    def update_embeddings(self, project_name: str, diagram_type: str, embeddings: Dict[str, List[float]]):
        self._check_connection()
        try:
            for entity_id, embedding in embeddings.items():
                if not isinstance(embedding, list) or not all(isinstance(x, float) for x in embedding):
                    raise ValueError(f"Invalid embedding format for entity {entity_id}")

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
                updated_count = result.consume().counters.properties_set
                logger.info(f"Updated embeddings for {updated_count} entities")
            return updated_count
        except Neo4jError as e:
            logger.error(f"Neo4j error in update_embeddings: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in update_embeddings: {str(e)}")
            raise

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
        try:
            with self.driver.session() as session:
                result = session.run(query, similarities=similarities)
                logger.info(
                    f"Created or updated {result.consume().counters.relationships_created} similarity relationships")
        except Neo4jError as e:
            logger.error(f"Neo4j error in update_similarity_relationships: {str(e)}")
            raise

    @staticmethod
    def _neo4j_update_similarity_relationships(tx, similarities: List[Dict[str, Any]]):
        query = """
        UNWIND $similarities AS sim
        MATCH (e1:Entity {id: sim.id1}), (e2:Entity {id: sim.id2})
        MERGE (e1)-[r:SIMILAR_TO]->(e2)
        SET r.score = sim.combined_similarity,
            r.embedding_similarity = sim.embedding_similarity,
            r.keyword_similarity = sim.keyword_similarity
        """
        return tx.run(query, similarities=similarities)

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

    @staticmethod
    def _neo4j_create_entire_project(tx, project_name: str, diagram_data: Dict[str, List[Dict[str, Any]]]):
        query = """
          MERGE (p:Project {name: $project_name})
          WITH p
          UNWIND $diagram_data AS diagram
          MERGE (d:Diagram {type: diagram.type, project: p.name})
          MERGE (p)-[:HAS_DIAGRAM]->(d)
          WITH d, diagram
          UNWIND diagram.entities AS entity
          MERGE (e:Entity {id: entity.id})
          SET e += entity
          MERGE (d)-[:CONTAINS_ENTITY]->(e)
          WITH e, entity
          UNWIND coalesce(entity.keywords, []) AS keyword
          MERGE (k:Keyword {name: keyword})
          MERGE (e)-[:HAS_KEYWORD]->(k)
          """
        tx.run(query, project_name=project_name,
               diagram_data=[{"type": k, "entities": v} for k, v in diagram_data.items()])

    def create_entire_project(self, project_name: str, diagram_data: Dict[str, List[Dict[str, Any]]]):
        try:
            with self.driver.session() as session:
                session.execute_write(self._neo4j_create_entire_project, project_name, diagram_data)
            logger.info(f"Successfully created entire project: {project_name}")
        except Neo4jError as e:
            logger.error(f"Neo4j error in create_entire_project: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_entire_project: {str(e)}")
            raise

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