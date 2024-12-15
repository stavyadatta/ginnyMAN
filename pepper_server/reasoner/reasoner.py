import traceback

from utils import Neo4j, PersonDetails, message_format
from core_api import Llama

class _Reasoner:
    def __init__(self):
        """
            Initializing the reasoner
            :param llama_url: Endpoint for the llama.cpp
        """
        pass

    def _developing_reasoning_prompt(self):
        system_reasoner = """
        You are an agent programmed to respond strictly according to the following rules:

        1. If the user explicitly asks you to "speak," you must respond with "speak"
        2. If the user explicitly asks you to "be silent," you must respond with "silent"
        3. If the user asks something that would require vision to answer (e.g., "what's in my hand," "how do you think I look"), you must respond with "vision"
        4. If the user gives no input or provides very small or meaningless input, respond with "bad input"
        5. For any other input or scenario, respond with "no change"

        You must not deviate from these rules or provide any additional explanation or context in your responses.
        This is a strict instruction.
        """
        # system_reasoner = """
        # You are an agent programmed to respond strictly according to the following rules:
        #
        # 1. If the user explicitly asks you to "speak," you must respond with "speak"
        # 2. If the user explicitly asks you to "be silent," you must respond with "silent"
        # 3. If the user asks something that would require vision to answer (e.g., "what's in my hand," "how do you think I look"), you must respond with "vision"
        # 4. For any other input or scenario, respond with "no change"
        #
        # You must not deviate from these rules or provide any additional explanation or context in your responses.
        # This is a strict instruction.
        # """

        system_dict = message_format("system", system_reasoner)
        return [system_dict]

    def _developing_user_prompt(self, text: str):
        user_prompt = message_format("user", text)
        return [user_prompt]

    def __call__(self, transcription, face_id: str, img=None) -> PersonDetails:
        """
            Running the reasoner and deciding on what APIs need to be run 
            with the reasoner program
            :param text: using the text to prompt the llm on what to do 
            :param face_id: To identify faces for doing an action
            :param img: for the VLM to get more context
        """
        try:
            system_prompt = self._developing_reasoning_prompt()
            person_details = Neo4j.get_person_details(face_id)
            if not person_details:
                Neo4j.create_or_update_person(face_id=face_id)
                person_details = Neo4j.get_person_details(face_id)
            user_prompt = self._developing_user_prompt(transcription)
            total_prompt = system_prompt + user_prompt

            response = Llama.send_to_model(total_prompt, stream=False)
            response_text = response.choices[0].message.content
            print(f"The Reasoner response is {response_text}\n")
            if response_text != "no change":
                print("Is the state inside coming as no change?", response_text)
                person_details.set_attribute("state", response_text)
            person_details.add_message(user_prompt[0])
            return person_details

        except Exception as e:
            print(f"Error in reasoning section: {e}")
            traceback.print_exc()
            raise Exception(e)


