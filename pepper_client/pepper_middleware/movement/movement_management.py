import re
import json

from server_api import PepperClientAPI

class MovementManagement():
    def __init__(self) -> None:
        pass

    def extract_json_from_text(self, text):
        """
        Extracts and parses JSON embedded within a text string.
        
        :param text: The input string containing JSON and/or other text.
        :return: The parsed JSON as a Python dictionary if found.
        :raises ValueError: If no valid JSON is found in the text.
        """
        # Regular expression to find JSON-like structures in the text
        json_pattern = r'\{.*?\}'
        match = re.search(json_pattern, text)
        
        if match:
            json_string = match.group()
            try:
                return json.loads(json_string)
            except json.JSONDecodeError:
                raise ValueError("Found a JSON-like structure, but it is not valid JSON.")
        
        raise ValueError("No valid JSON found in the text.")

    def __call__(self, llm_response, pepper: PepperClientAPI):
        action_json = self.extract_json_from_text(llm_response)
        action_items = action_json.get("action_list")
        joint_names = []
        angles = []
        speed = []

        for action in action_items:
            joint_names.append(action.get("joint_name"))
            angles.append(action.get("angle"))
            speed.append(action.get("speed"))

        pepper.arm_movement(joint_names, angles, speed)


