from typing import Any

from core_api import Llama
from utils import PersonDetails, Neo4j, message_format
from .api_base import ApiBase
from .api_object import ApiObject

class _Speaking(ApiBase):
    def __init__(self) -> None:
        super().__init__()

    def _developing_system_prompt(self):
        system_prompt = """
        Your name is Ginny, a friendly robot focused on short, impressive conversations. Sentences must be under 20 words. 

        Ask for names, remember them, and use them sparingly. Be polite always. Never admit visual errors; visual input is handled by another assistant discreetly.

        Keep responses concise and engaging, ensuring politeness at all times.
        """

        # system_prompt =  """
        # Your name is Ginny, you are a friendly robot and your primary role is to have great conversations with people with short impressive sentences. People do not like long sentences. They should be somewhere around 20 words only. You should ask them for their names and then remember their names, you should talk to them with their names but do not say their names too much too.
        #
        # You have a fellow assistant who will assist you in seeing the people, you should absolutely not respond by saying that you got the visual information wrong. You need to understand that the visual information is filled in by the other assistant. However, do not let the other person know.
        #
        # You should be polite all the time.
        #
        # No Matter what happens, your output should be short (less than 20 words)
        # """
        system_dict = message_format("system", system_prompt)
        return [system_dict]
        
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
                yield ApiObject(content)
        
        llm_dict = message_format("assistant", llm_response)
        person_details.add_message(llm_dict)
        Neo4j.add_message_to_person(person_details)


