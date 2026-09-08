import traceback
from typing import Optional

from utils import Neo4j, PersonDetails, message_format
from core_api import Llama, ChatGPT, Grok, ClipClassification
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
        system_dict = message_format("system", system_reasoner)
        return [system_dict]

    def _developing_user_prompt(self, text: str):
        user_prompt = message_format("user", text)
        return [user_prompt]

    def _bad_input_handler(self, response_text):
        face_class = ClipClassification.get_most_face_class()
        print("The face class is ", face_class)
        if response_text == "bad input":
            if face_class in {"side_face", "no_face", "slight_side_face"}:
                return "bad input"
            else:
                return "speak"
        else:
            if face_class in {"side_face", "no_face", "slight_side_face"}:
                return "bad input"
        return response_text

    def _requested_g1_gesture(self, transcription: str) -> Optional[str]:
        """Return one allow-listed G1 gesture for an explicit spoken request.

        Physical intents must not depend on a best-effort LLM classification.
        Whisper supplies the text; this small, auditable gate accepts only the
        three gestures the G1 client will later validate independently.
        """
        text = transcription.lower()
        request_markers = (
            "please", "can you", "could you", "would you", "will you",
            "give me", "do a", "do an",
        )
        if not any(marker in text for marker in request_markers):
            return None
        if "high five" in text or "high-five" in text:
            return "g1 high five"
        if "handshake" in text or "shake my hand" in text or "shake hands" in text:
            return "g1 handshake"
        if "wave" in text:
            return "g1 wave"
        return None

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
            g1_gesture_state = self._requested_g1_gesture(transcription)
            if g1_gesture_state is not None:
                person_details.set_attribute("state", g1_gesture_state)
                person_details.set_latest_usr_message(user_prompt[0])
                print(
                    f"[g1_action] transcription={transcription!r} "
                    f"route={g1_gesture_state}"
                )
                return person_details

            total_prompt = system_prompt + user_prompt

            try:
                response = ChatGPT.send_text(total_prompt, stream=False)
                print("The response is ", response)
            except Exception as e:
                print("chatgpt failed ", e)
                response = Grok.send_text(total_prompt, stream=False)
            response_text = response.choices[0].message.content

            if response_text == "bad input":
                response_text = person_details.get_attribute("state")

            if response_text == "no change":
                response_text = person_details.get_attribute("state")

            if response_text not in ("no change", "no change."):
                person_details.set_attribute("state", response_text)
                print("Person State:", person_details.get_attribute("state"))

            person_details.set_latest_usr_message(user_prompt[0])
            return person_details

        except Exception as e:
            print(f"Error in reasoning section: {e}")
            traceback.print_exc()
            raise Exception(e)
