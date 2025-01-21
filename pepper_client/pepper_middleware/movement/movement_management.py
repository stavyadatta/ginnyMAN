import re
import json

class _MovementManagement():
    def __init__(self):
        pass

    def extract_json_from_text(self, text):
        """
        Extracts and parses JSON embedded within a text string.
        
        :param text: The input string containing JSON and/or other text.
        :return: The parsed JSON as a Python dictionary if found.
        :raises ValueError: If no valid JSON is found in the text.
        """
        # Regular expression to find JSON-like structures in the text
        try:
            print("Well trying the json loads thingy")
            return json.loads(text)
        except json.JSONDecodeError:
            print("Entering the error")
            raise ValueError("Found a JSON-like structure, but it is not valid JSON.")
        
        raise ValueError("No valid JSON found in the text.")

    def __call__(self, llm_response, pepper):
        print("The thing is getting valled yes")
        action_json = self.extract_json_from_text(llm_response)
        print("The json action is \n \n \n \n ", action_json)
        action_items = action_json.get("action_list")
        joint_names = []
        angles = []
        speed = []

        for action in action_items:
            joint_names.append(action.get("joint_name"))
            angles.append(action.get("angle"))
            speed.append(action.get("speed"))

        print("Highfice dictionary ", joint_names, angles, speed)
        pepper.arm_movement(joint_names, angles, speed)


