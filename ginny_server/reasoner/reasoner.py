import traceback
import random
import re
from difflib import SequenceMatcher
from typing import Optional

from utils import Neo4j, PersonDetails, message_format
from core_api import Llama, ChatGPT, Grok, ClipClassification
from .prompt import action_reasoner_prompt

# The reasoner LLM classifies intent into a *family* of gestures ("g1
# greeting", "g1 farewell") rather than one specific action, so the family
# can be resolved to one of its concrete states by weighted probability
# instead of always picking the same gesture. Equal weights today; skew
# them (or add more entries) without touching the resolution logic.
_GREETING_GESTURE_WEIGHTS = {"g1 wave": 0.5, "g1 handshake": 0.5}
_FAREWELL_GESTURE_WEIGHTS = {"g1 blow kiss left": 0.5, "g1 blow kiss right": 0.5}
_GESTURE_FAMILY_WEIGHTS = {
    "g1 greeting": _GREETING_GESTURE_WEIGHTS,
    "g1 farewell": _FAREWELL_GESTURE_WEIGHTS,
}


def _weighted_choice(options: dict) -> str:
    """Pick one key from options, weighted by its probability value."""
    return random.choices(list(options.keys()), weights=list(options.values()), k=1)[0]


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
        system_reasoner = action_reasoner_prompt
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

    def _uncertain_g1_gesture(self, transcription: str) -> Optional[str]:
        """Return a confirmation-only gesture candidate, never an action."""
        text = transcription.lower()
        request_markers = (
            "please", "can you", "could you", "would you", "will you",
            "give me", "do a", "do an",
        )
        if not any(marker in text for marker in request_markers):
            return None
        words = re.findall(r"[a-z]+", text)
        # "wait" and "wave" are acoustically close on G1's noisy microphone.
        # A near match only asks a question; it can never move the robot.
        if any(SequenceMatcher(None, word, "wave").ratio() >= 0.75
               for word in words):
            return "g1 wave"
        if "shake" in words:
            return "g1 handshake"
        if "five" in words and any(word in {"hi", "high"} for word in words):
            return "g1 high five"
        return None

    def _confirmed_g1_gesture(self, transcription: str) -> bool:
        """Accept only a small explicit confirmation vocabulary."""
        text = " ".join(re.findall(r"[a-z]+", transcription.lower()))
        return text in {"yes", "yes please", "yeah", "yep", "correct", "do it", "please do"}

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
            pending_state = str(person_details.get_attribute("state"))
            if pending_state.startswith("g1 confirm "):
                pending_gesture = pending_state.removeprefix("g1 confirm ")
                if self._confirmed_g1_gesture(transcription):
                    person_details.set_attribute("state", "g1 " + pending_gesture)
                    person_details.set_latest_usr_message(user_prompt[0])
                    print(
                        f"[g1_action] confirmation={transcription!r} "
                        f"route=g1 {pending_gesture}"
                    )
                    return person_details
                # Do not allow an abandoned question to trap future ordinary
                # conversation in confirmation mode.
                person_details.set_attribute("state", "speak")

            g1_gesture_state = self._requested_g1_gesture(transcription)
            if g1_gesture_state is not None:
                person_details.set_attribute("state", g1_gesture_state)
                person_details.set_latest_usr_message(user_prompt[0])
                print(
                    f"[g1_action] transcription={transcription!r} "
                    f"route={g1_gesture_state}"
                )
                return person_details

            uncertain_gesture = self._uncertain_g1_gesture(transcription)
            if uncertain_gesture is not None:
                person_details.set_attribute(
                    "state", "g1 confirm " + uncertain_gesture.removeprefix("g1 ")
                )
                person_details.set_latest_usr_message(user_prompt[0])
                print(
                    f"[g1_action] transcription={transcription!r} "
                    f"confirmation_needed={uncertain_gesture}"
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

            gesture_family = _GESTURE_FAMILY_WEIGHTS.get(response_text)
            if gesture_family is not None:
                resolved_gesture = _weighted_choice(gesture_family)
                print(
                    f"[g1_action] llm_category={response_text!r} "
                    f"resolved={resolved_gesture}"
                )
                response_text = resolved_gesture

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
