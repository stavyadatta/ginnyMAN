from fuzzywuzzy import fuzz

from .api_object import ApiObject
from .person_details import PersonDetails
from .neo4j_db import _Neo4j
from .secondary_details import SecondaryDetails
from .g1_action import (
    ACTION_NONE,
    ACTION_SCRATCH_HEAD,
    G1_ACTION_ERROR_MODE,
    G1_ACTION_MODE,
    g1_action_payload,
)

Neo4j = _Neo4j()

def message_format(role: str, content: str):
    return {"role": role, "content": content}

STATE_SPEAK = "speak"


def record_assistant_reply(person_details, reply: str, next_state: str = STATE_SPEAK):
    """Persist one assistant turn and the state the robot returns to.

    Every API that answers and then hands the floor back to conversation ends
    this way, so the order (remember the reply, set the next state, then
    write) lives here rather than in each API.
    """
    person_details.set_latest_llm_message(message_format("assistant", reply))
    person_details.set_attribute("state", next_state)
    Neo4j.add_message_to_person(person_details)


def name_similarity(name_1, name_2):
    """ 
        Fuzzy search to find similarity between two names
    """
    return fuzz.ratio(name_1, name_2)


__all__ = [
    "ACTION_NONE",
    "ACTION_SCRATCH_HEAD",
    "ApiObject",
    "G1_ACTION_ERROR_MODE",
    "G1_ACTION_MODE",
    "Neo4j",
    "PersonDetails",
    "STATE_SPEAK",
    "SecondaryDetails",
    "g1_action_payload",
    "message_format",
    "record_assistant_reply",
]
