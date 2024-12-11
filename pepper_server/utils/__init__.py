from .neo4j_db import _Neo4j
from .media_manager import MediaManager
from .person_details import PersonDetails

Neo4j = _Neo4j()

def message_format(role: str, content: str):
    return {"role": role, "content": content}

__all__ = ["Neo4j", "MediaManager", "PersonDetails", "message_format"]





