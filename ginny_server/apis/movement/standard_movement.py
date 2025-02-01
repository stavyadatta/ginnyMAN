from core_api import ChatGPT
from utils import PersonDetails, Neo4j, message_format, ApiObject

from ..api_base import ApiBase
from .standard_prompt import movement_prompt

class _StandardMovement(ApiBase):
    def __init__(self) -> None:
        super().__init__()

    def _developing_system_prompt(self):
        system_prompt = movement_prompt
        system_dict = message_format("system", system_prompt)
        return [system_dict]

    def __call__(self, person_details: PersonDetails):
        messages = person_details.get_attribute("messages")
        system_dict = self._developing_system_prompt()
        total_prompt = system_dict + [messages[-1]]

        response = ChatGPT.send_text_get_json(total_prompt, stream=False, max_tokens=2000)

        print(response.choices[0].message.content)
        yield ApiObject(response.choices[0].message.content, mode='standard_movement') 

        llm_dict = message_format("assistant", "The movement has been performed")
        person_details.add_message(llm_dict)
        person_details.set_attribute("state", "speak")
        Neo4j.add_message_to_person(person_details)
