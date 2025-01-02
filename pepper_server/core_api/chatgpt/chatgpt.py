import os
import openai
import base64
import cv2
import numpy as np

class _OpenAIHandler:
    def __init__(self, model_name="gpt-4"):
        """
        Initialize the OpenAIHandler.

        :param model_name: The model name to use, e.g., "gpt-4"
        """
        self.client = openai.OpenAI()

    def _encode_image(self, image):
        """
        Encode an image into base64 format for processing.

        :param image: NumPy array (from cv2), image path, or file-like object
        :return: Base64 encoded image string
        """
        if isinstance(image, np.ndarray):
            _, buffer = cv2.imencode(".png", image)
            encoded_image = base64.b64encode(buffer).decode("utf-8")
        elif isinstance(image, str):
            with open(image, "rb") as img_file:
                encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
        else:
            encoded_image = base64.b64encode(image.read()).decode("utf-8")

        return encoded_image

    def process_image_and_text(self, image, person_details, max_tokens=1000):
        """
        Process an image and text prompt using OpenAI API with streaming.

        :param image: NumPy array (from cv2), image path, or file-like object
        :param person_details: An object with a `get_attribute` method for accessing messages
        :param max_tokens: Maximum tokens for response
        :yield: Streaming response chunks
        """
        # Encode the image
        img_base64 = self._encode_image(image)
        all_but_last_message = person_details.get_attribute("messages")[:-1]
        last_message = person_details.get_attribute("messages")[-1]

        # Develop the last message including the image
        last_dict = self.develop_last_message(last_message, img_base64)

        # Create the system prompt
        system_prompt = self._develop_system_prompt()

        # Combine messages for the API call
        total_prompt = all_but_last_message + [last_dict]

        try:
            # Start streaming response
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *total_prompt
                ],
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except openai.OpenAIError as e:
            yield f"API Error: {str(e)}"
        except Exception as e:
            yield f"Unexpected Error: {str(e)}"

    def develop_last_message(self, last_message, img_base64):
        """
        Create the last message dictionary with the image included.

        :param last_message: Last message details
        :param img_base64: Base64 encoded image string
        :return: Updated last message dictionary
        """
        return {
            "role": last_message.get("role"),
            "content": [
                {
                    "type": "text",
                    "text": last_message.get("content")
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_base64}"
                    }
                }
            ]
        }

    def _develop_system_prompt(self):
        """
        Generate the system-level prompt.

        :return: System prompt string
        """
        robot_description = (
        "You are part of Ginny Robot, a friendly robot assistant who excels at talking. However, Ginny Robot does not have vision, "
        "and you assist with the visual component. Describe images accurately but avoid explicitly stating that you are describing an image. "
        "Focus on generic features and ensure you do not violate copyright laws. Avoid mentioning that you cannot generate copyrighted material.\n\n"
        "Be courteous and concise, as people prefer shorter sentences. If given names of individuals, remember them and use their names naturally. "
        "Speak like a human, keeping your descriptions engaging and natural.\n\n"
        "Ensure your sentences are short yet impressive. When referring to an image or photo, replace those words with phrases like 'I see...'."
        )

        return robot_description

