"""Shared body of the two movement APIs.

Custom and standard movement differ only in which prompt describes the
available motions and which mode label the robot client reads. Everything
else — ask the model for JSON, hand it over, then return to conversation —
is one behaviour, so it is written once.
"""

from typing import Any

from core_api import ChatGPT
from utils import PersonDetails, ApiObject, message_format, record_assistant_reply

from ..api_base import ApiBase

# Joint-angle JSON for a whole sequence runs long; a short cap truncates the
# movement mid-pose and the client rejects the payload.
MOVEMENT_MAX_TOKENS = 2000

MOVEMENT_PERFORMED_REPLY = "The movement has been performed"


class _MovementApi(ApiBase):
    """Turn a spoken movement request into the client's movement JSON."""

    #: Prompt listing the motions this API may emit. Subclasses must set it.
    movement_prompt: str = ""
    #: Mode label the robot client dispatches on. Subclasses must set it.
    response_mode: str = ""

    def _developing_system_prompt(self):
        system_dict = message_format("system", self.movement_prompt)
        return [system_dict]

    def __call__(self, person_details: PersonDetails) -> Any:
        latest_usr_message = person_details.get_latest_user_message()
        total_prompt = self._developing_system_prompt() + [latest_usr_message]

        print("The total prompt is ", total_prompt)
        response = ChatGPT.send_text_get_json(
            total_prompt, stream=False, max_tokens=MOVEMENT_MAX_TOKENS
        )

        movement_json = response.choices[0].message.content
        print(movement_json)
        yield ApiObject(movement_json, mode=self.response_mode)

        record_assistant_reply(person_details, MOVEMENT_PERFORMED_REPLY)
