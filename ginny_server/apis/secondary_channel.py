from .api_object import ApiObject
from .api_base import ApiBase

from utils import PersonDetails, Neo4j, message_format
from core_api import ChatGPT

class _SecondaryChannel(ApiBase):
    def __init__(self):
        super().__init__()

    def _developing_system_prompt(self):
        system_prompt = """ 
        Identify the object that they are referring to and only respond to the object 

        for example 

        Input: find me the phone
        Output: {
        'api_name': 'ObjectLookup',
        'api_details': {
                'object_name': 'laptop'
            }
        }

        Input: Where is my laptop
        Output: {
        'api_name': 'ObjectLookup',
        'api_details': {
                'object_name': 'laptop'
            }
        }

        Input: Can you find my glasses
        Output: {
        'api_name': 'ObjectLookup',
        'api_details': {
                'object_name': 'glasses'
            }
        }
        """
        system_dict = message_format("system", system_prompt)
        return [system_dict]

    def __call__(self, person_details: PersonDetails):
        messages = person_details.get_attribute("messages")
        system_dict = self._developing_system_prompt()
        total_prompt = system_dict + [messages[-1]]

        response = ChatGPT.send_text_get_json(total_prompt, stream=False)
        print(response.choices[0].message.content)
        yield ApiObject(response.choices[0].message.content, mode='secondary') 

        llm_response = response.choices[0].message.content
        llm_dict = message_format("assistant", llm_response)
        person_details.add_message(llm_dict)
        person_details.set_attribute("state", "speak")
        Neo4j.add_message_to_person(person_details)


