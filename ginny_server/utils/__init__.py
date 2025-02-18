from .api_object import ApiObject
from .person_details import PersonDetails
from .neo4j_db import _Neo4j
from .secondary_details import SecondaryDetails

Neo4j = _Neo4j()

def message_format(role: str, content: str):
    return {"role": role, "content": content}

__all__ = ["Neo4j", "PersonDetails", "message_format", "SecondaryDetails", "ApiObject"]





