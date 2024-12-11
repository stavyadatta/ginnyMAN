from typing import Any

from core_api import Llama
from utils import PersonDetails, Neo4j, message_format
from .api_base import ApiBase

class _Speaking(ApiBase):
    def __init__(self) -> None:
        super().__init__()

    def _developing_system_prompt(self):
        system_prompt = "You are a helpful assistant (strictly under 20 words)."
        system_dict = [{"role": "system", "content": system_prompt}]
        return system_dict
        
    def __call__(self, person_details: PersonDetails) -> Any:
        messages = person_details.get_attribute("messages")
        system_dict = self._developing_system_prompt()
        total_prompt = system_dict + messages
        
        response = Llama.send_to_model(total_prompt, stream=True)

        llm_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                llm_response += content
                yield content
        
        llm_dict = message_format("llm", llm_response)
        person_details.add_message(llm_dict)
        Neo4j.add_message_to_person(person_details)


