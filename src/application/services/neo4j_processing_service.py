import logging
import json
from typing import Dict, Any, List
from src.adapters.persistence.neo4j_persistence_adapter import Neo4jPersistenceAdapter
from src.application.services.project_management_service import ProjectManagementService
from src.application.services.similarity_processing_service import SimilarityService
from src.domain.ports.embedding_adapter_protocol import EmbeddingAdapterProtocol
from src.domain.ports.neo4j_persistence_adapter_protocol import Neo4jPersistenceAdapterProtocol

logger = logging.getLogger("uvicorn.error")


def _process_json_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"JSON file processed successfully: {file_path}")
        logger.debug(f"JSON content: {data}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file {file_path}: {str(e)}")
        raise
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing JSON file {file_path}: {str(e)}")
        raise


class Neo4jProcessingService:
    def __init__(self, project_manager: ProjectManagementService,
                 embedding_adapter: EmbeddingAdapterProtocol,
                 neo4j_adapter: Neo4jPersistenceAdapterProtocol,
                 similarity_service: SimilarityService):
        self.project_manager = project_manager
        self.embedding_adapter = embedding_adapter
        self.neo4j_adapter = neo4j_adapter
        self.similarity_service = similarity_service

    @staticmethod
    def _add_temp_ids_to_entities(entities: List[Dict[str, Any]], diagram_type: str) -> List[Dict[str, Any]]:
        return [
            {**entity, 'id': entity.get('id', f"{diagram_type}_{index}")}
            for index, entity in enumerate(entities)
        ]

    async def process_neo4j_data(self, project_name: str, diagram_type: str) -> Dict[str, Any]:
        try:
            logger.info(f"Starting Neo4j data processing for project: {project_name}, diagram: {diagram_type}")
            
            # Récupérer les informations du projet et le chemin des entités
            project = self.project_manager.find_project(project_name)
            entities_path = self.project_manager.get_project_entities_path(project_name, diagram_type)
            
            # Traiter le fichier JSON pour obtenir les entités et les relations
            data = _process_json_file(entities_path)
            entities = self._add_temp_ids_to_entities(data['entities'], diagram_type)
            relationships = data.get('relationships', [])
            
            # Obtenir les embeddings pour les entités
            embeddings = self.embedding_adapter.get_embeddings_dict(entities, diagram_type)
            
            # Récupérer toutes les entités pour le calcul des similarités
            all_entities = self.neo4j_adapter.get_entities_for_similarity(project_name)
            similarities = self.similarity_service.calculate_similarities(all_entities)
            
            # Appel des fonctions individuelles dans l'ordre correct
            self.neo4j_adapter.create_or_update_project(project_name, project['type'])  # Créer ou mettre à jour le projet
            self.neo4j_adapter.create_or_update_diagram(project_name, diagram_type)     # Créer ou mettre à jour le diagramme
            self.neo4j_adapter.create_or_update_entities_and_keywords(project_name, diagram_type, entities)  # Créer ou mettre à jour les entités et les mots-clés
            self.neo4j_adapter.update_embeddings(project_name, diagram_type, embeddings)  # Mettre à jour les embeddings
            self.neo4j_adapter.create_relationships(project_name, diagram_type, relationships)  # Créer les relations
            self.neo4j_adapter.update_similarity_relationships(similarities)  # Mettre à jour les relations de similarité
            
            logger.info(f"Neo4j data processing completed for project: {project_name}, diagram: {diagram_type}")
            return {"status": "completed", "message": f"Neo4j data processing completed for {project_name}, {diagram_type}"}
        except Exception as e:
            logger.error(f"Error during Neo4j data processing: {str(e)}")
            return {"status": "failed", "message": f"Neo4j data processing failed for {project_name}, {diagram_type}. Error: {str(e)}"}


    async def process_entire_project(self, project_name: str) -> Dict[str, Any]:
        try:
            logger.info(f"Starting Neo4j data processing for entire project: {project_name}")
            
            self.neo4j_adapter.ensure_vector_index()
            
            project = self.project_manager.find_project(project_name)
            diagram_types = self.project_manager.get_diagram_types()
            
            for diagram_type in diagram_types:
                logger.info(f"Processing diagram type: {diagram_type}")
                result = await self.process_neo4j_data(project_name, diagram_type)
                if result['status'] == 'error':
                    return result  # Si une erreur se produit, on arrête le traitement
            
            logger.info(f"Neo4j data processing completed for entire project: {project_name}")
            return {"status": "completed",
                    "message": f"Neo4j data processing completed for entire project {project_name}"}
        
        except Exception as e:
            logger.exception(f"Error during Neo4j data processing for entire project: {str(e)}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
