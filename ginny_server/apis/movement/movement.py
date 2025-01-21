from typing import Any

from core_api import ChatGPT, Llama, Grok
from ..api_object import ApiObject
from ginny_server.utils import PersonDetails, Neo4j, message_format

from .prompt import movement_prompt
from ..api_base import ApiBase

class _Movement(ApiBase):
    def __init__(self) -> None:
        super().__init__()

    def _developing_system_prompt(self):
        # system_prompt =  """
        # Your name is Ginny, you are a friendly robot and your primary role is to have great conversations with people with short impressive sentences. People do not like long sentences. They should be somewhere around 20 words only. You should ask them for their names and then remember their names, you should talk to them with their names but do not say their names too much too.
        #
        # You have a fellow assistant who will assist you in seeing the people, you should absolutely not respond by saying that you got the visual information wrong. You need to understand that the visual information is filled in by the other assistant. However, do not let the other person know.
        #
        # You should be polite all the time.
        # Here you are asked to do a movement, the movement is going to execute 
        # donot worry about it. donot say that you are text based model and you cannot 
        # execute the movement
        # """
        system_prompt = movement_prompt
        system_dict = message_format("system", system_prompt)
        return [system_dict]
        
    def __call__(self, person_details: PersonDetails) -> Any:
        messages = person_details.get_attribute("messages")
        system_dict = self._developing_system_prompt()
        total_prompt = system_dict + [messages[-1]]
        
        print("The total prompt is ", total_prompt)
        # response = Llama.send_to_model(total_prompt, stream=False)
        response = ChatGPT.send_text_get_json(total_prompt, stream=False)

        print(response.choices[0].message.content)
        yield ApiObject(response.choices[0].message.content, movement=True) 

        llm_response = response.choices[0].message.content
        # for chunk in response:
        #     if chunk.choices[0].delta.content is not None:
        #         content = chunk.choices[0].delta.content
        #         llm_response += content
        #         yield ApiObject(content, movement=True)
        
        llm_dict = message_format("assistant", llm_response)
        person_details.add_message(llm_dict)
        person_details.set_attribute("state", "speak")
        Neo4j.add_message_to_person(person_details)


