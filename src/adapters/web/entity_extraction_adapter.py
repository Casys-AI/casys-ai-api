# src/adapters/web/entity_extraction_adapter.py
import logging
import json
import re
from langchain.prompts import ChatPromptTemplate
from src.domain.ports.entity_extraction_port import EntityExtractionPort

import logging
import json
import re
from typing import Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate
from src.domain.ports.entity_extraction_port import EntityExtractionPort

logger = logging.getLogger(__name__)

class EntityExtractionAdapter(EntityExtractionPort):
    def __init__(self, openai_chat):
        self.openai_chat = openai_chat

    def extract_entities_and_relationships(self, diagram_content: str) -> Dict[str, Any]:
        try:
            prompt = self._create_prompt_template()
            chain = prompt | self.openai_chat
            result = chain.invoke({"content": diagram_content})
            return self._process_result(result.content)
        except Exception as e:
            logger.exception(f"Erreur lors de l'extraction des entités et relations : {str(e)}")
            return {"entities": [], "relationships": []}

    def _create_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template("""
        Analysez le contenu suivant et extrayez les entités et leurs relations :

        {content}

        Fournissez la sortie au format JSON avec la structure suivante :
        {{
            "entities": [
                {{
                    "name": "<nom_entité>",
                    "type": "<type_entité>",
                    "description": "<description_entité>",
                    "keywords": ["<mot_clé1>", "<mot_clé2>", ...]
                }},
                ...
            ],
            "relationships": [
                {{
                    "source": "<entité_source>",
                    "target": "<entité_cible>",
                    "type": "<type_relation>"
                }},
                ...
            ]
        }}

        Assurez-vous que la sortie est un JSON valide sans aucun texte supplémentaire.
        """)

    def _process_result(self, result_content: str) -> Dict[str, Any]:
        try:
            json_content = self._extract_json_content(result_content)
            if json_content:
                parsed_content = json.loads(json_content)
                self._log_extraction_results(parsed_content)
                return parsed_content
            else:
                logger.error("Aucun contenu JSON trouvé dans la réponse")
                return {"entities": [], "relationships": []}
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du décodage JSON : {e}")
            logger.error(f"Contenu reçu : {result_content}")
            return {"entities": [], "relationships": []}

    def _extract_json_content(self, content: str) -> Optional[str]:
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        return json_match.group() if json_match else None

    def _log_extraction_results(self, parsed_content: Dict[str, Any]) -> None:
        entity_count = len(parsed_content.get("entities", []))
        relationship_count = len(parsed_content.get("relationships", []))
        logger.info(f"Extraction réussie : {entity_count} entités et {relationship_count} relations trouvées")
        logger.debug(f"Contenu extrait : {json.dumps(parsed_content, indent=2)}")