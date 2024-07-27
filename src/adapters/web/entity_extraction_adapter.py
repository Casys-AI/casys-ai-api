# src/adapters/web/entity_extraction_adapter.py
import logging
import json
import re
from langchain.prompts import ChatPromptTemplate
from src.domain.ports.entity_extraction_port import EntityExtractionPort

logger = logging.getLogger(__name__)


class EntityExtractionAdapter(EntityExtractionPort):
    def __init__(self, openai_chat):
        self.openai_chat = openai_chat

    def extract_entities_and_relationships(self, diagram_content):
        prompt = ChatPromptTemplate.from_template("""
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

        chain = prompt | self.openai_chat
        result = chain.invoke({"content": diagram_content})

        try:
            json_content = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_content:
                return json.loads(json_content.group())
            raise ValueError("Aucun contenu JSON trouvé dans la réponse")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du décodage JSON : {e}")
            logger.error(f"Contenu reçu : {result.content}")
            return {"entities": [], "relationships": []}


