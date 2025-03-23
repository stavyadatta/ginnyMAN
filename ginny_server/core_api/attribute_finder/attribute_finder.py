import json
from threading import Thread
from queue import Queue

from utils import PersonDetails, Neo4j, message_format
from .prompt import get_attr_prompt

class _AttributeFinder():
    def __init__(self) -> None:
        self.possible_attr_queue: Queue[PersonDetails] = Queue()
        
        attribute_thread = Thread(
            target=self.attr_checker,
            daemon=True
        )

        attribute_thread.start()

    def adding_text2attr_finder(self, person_details: PersonDetails):
        self.possible_attr_queue.put(person_details)

    def attr_checker(self):
        while True:
            person_details = self.possible_attr_queue.get()
            text_message = person_details.get_latest_user_message()
            person_attributes = person_details.get_attribute("attributes")
            face_id = person_details.get_attribute("face_id")

            from core_api import ChatGPT

            system_text = get_attr_prompt(person_attributes)
            system_message = message_format("system", system_text)
            total_messages = [system_message, text_message]

            try:
                response = ChatGPT.send_text_get_json(total_messages, stream=False)
            except Exception:
                print("Chatgpt failed to get attributes")
                continue

            output = response.choices[0].message.content
            output_json = json.loads(output)

            output_attribute = output_json.get("attribute")
            input_name = output_json.get("name")

            attribute_bool = bool(output_attribute)
            name_bool = bool(input_name)
            face_id = person_details.get_attribute("face_id")

            # Adding the attribute to the existing attributes list
            person_attributes.append(output_attribute)

            if attribute_bool or name_bool:
                Neo4j.update_name_attribute(face_id=face_id, 
                                            name=input_name, 
                                            attributes=person_attributes
                                        )
