"""Safe, structured gesture intents for the Unitree G1 client.

This API intentionally does not know anything about robot joint angles or
Unitree action IDs.  It emits a small allow-listed intent which the G1 client
must validate and map to its own approved action implementation.
"""

import json

from utils import ApiObject, Neo4j, PersonDetails, message_format
from .api_base import ApiBase


# The reasoner may select only these states.  Keep replies short because the
# robot client can speak them before it performs the corresponding gesture.
G1_GESTURES = {
    "g1 wave": {
        "action": "wave",
        "reply": "Hello! It is nice to meet you.",
    },
    "g1 handshake": {
        "action": "handshake",
        "reply": "Nice to meet you too.",
    },
    "g1 high five": {
        "action": "high_five",
        "reply": "High five!",
    },
}


class _G1Gesture(ApiBase):
    """Emit one G1 gesture contract instead of Pepper joint-angle JSON."""

    def __call__(self, person_details: PersonDetails):
        state = str(person_details.get_attribute("state"))
        gesture = G1_GESTURES.get(state)
        if gesture is None:
            # This should be unreachable when the reasoner prompt is obeyed.
            # Never substitute a guessed action when the state is unexpected.
            yield ApiObject(
                json.dumps({"reply": "", "action": ""}), mode="g1_action_error"
            )
            return

        payload = {
            "reply": gesture["reply"],
            "action": gesture["action"],
        }
        reply_message = message_format("assistant", gesture["reply"])
        person_details.set_latest_llm_message(reply_message)
        person_details.set_relevant_messages([reply_message])
        person_details.set_attribute("state", "speak")
        Neo4j.add_message_to_person(person_details)

        # TextChunk has no dedicated action field.  JSON plus mode is the
        # version-compatible contract consumed by the G1 C++ client.
        yield ApiObject(json.dumps(payload), mode="g1_action")
