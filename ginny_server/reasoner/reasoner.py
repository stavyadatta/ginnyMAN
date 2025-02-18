import traceback
from typing import Optional

from utils import Neo4j, PersonDetails, message_format
from core_api import Llama, ChatGPT, Grok
from .prompt import reasoner_prompt

class _Reasoner:
    def __init__(self):
        """
            Initializing the reasoner
            :param llama_url: Endpoint for the llama.cpp
        """
        pass

    def to_lowercase(self, input_string):
        """
        Converts all characters in the input string to lowercase.

        Parameters:
            input_string (str): The string to convert.

        Returns:
            str: The input string in lowercase.
        """
        return input_string.lower()

    def _developing_reasoning_prompt(self):
        system_reasoner = reasoner_prompt
        # system_reasoner = """
        # You are an agent programmed to respond strictly according to the following rules:
        #
        # 1. If the user explicitly asks you to "speak," or "talk," respond with "speak".
        # 2. If the user explicitly asks you to "be silent," respond with "silent".
        # 3. If the user asks a question requiring vision to answer (e.g., "what's in my hand," "how do you think I look"), respond with "vision".
        # 4. If the user provides no input or says "You" or "Thank you", respond with "bad input". Use it sparingly
        # 5. If the user asks to raise an arm, respond with "movement".
        # 6. For any other input or scenario, respond with "no change".
        # Examples under the delimitters
        #
        # Strictly follow these rules and provide no additional explanation or context in your responses.
        # """

        # system_reasoner = """
        # You are an agent programmed to respond strictly according to the following rules:
        #
        # 1. If the user explicitly asks you to "speak," or "talk," you must respond with "speak"
        # 2. If the user explicitly asks you to "be silent," you must respond with "silent"
        # 3. If the user asks something that would require vision to answer (e.g., "what's in my hand," "how do you think I look"), you must respond with "vision"
        # 4. If the user gives no input, says "You" or "Thank you", respond with "bad input"
        # 5. If the user asks to raise arm, you should respond with "movement"
        # 6. For any other input or scenario, respond with "no change"
        #
        # You must not deviate from these rules or provide any additional explanation or context in your responses. You must stick to above responses as commanded
        # This is a strict instruction.
        # """
        #
        system_dict = message_format("system", system_reasoner)
        return [system_dict]

    def _developing_user_prompt(self, text: str):
        user_prompt = message_format("user", text)
        return [user_prompt]

    def __call__(self, transcription, face_id: Optional[str], img=None) -> PersonDetails:
        """
            Running the reasoner and deciding on what APIs need to be run 
            with the reasoner program
            :param text: using the text to prompt the llm on what to do 
            :param face_id: To identify faces for doing an action
            :param img: for the VLM to get more context
        """
        if face_id is None:
            return PersonDetails({
                "state": "bad input" 
            })
        try:
            system_prompt = self._developing_reasoning_prompt()
            person_details = Neo4j.get_person_details(face_id)
            if not person_details:
                Neo4j.create_or_update_person(face_id=face_id)
                person_details = Neo4j.get_person_details(face_id)
            user_prompt = self._developing_user_prompt(transcription)
            total_prompt = system_prompt + user_prompt

            # response = Llama.send_to_model(total_prompt, stream=False)
            # response = ChatGPT.send_text(total_prompt, stream=False)
            try:
                response = Grok.send_text(total_prompt, stream=False)
            except Exception as e:
                print("grok failed ", e)
                response = ChatGPT.send_text(total_prompt, stream=False)
            response_text = response.choices[0].message.content
            if response_text not in ("no change", "no change."):
                print("State:", response_text)
                person_details.set_attribute("state", response_text)
            person_details.add_message(user_prompt[0])
            return person_details

        except Exception as e:
            print(f"Error in reasoning section: {e}")
            traceback.print_exc()
            raise Exception(e)


