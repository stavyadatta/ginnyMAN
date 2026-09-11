from utils import ApiObject, PersonDetails, record_assistant_reply
from core_api import PersonDetectionCropper, ChatGPT, Grok, RelationshipChecker

from .api_base import ApiBase

class _PersonAttribute(ApiBase):
    def __init__(self) -> None:
        super().__init__()

    def _describe_person(self, cropped_person, person_details):
        try:
            return ChatGPT.process_image_and_text(cropped_person, person_details)
        except Exception as e:
            print("chatgpt failed ", e)
            return Grok.process_image_and_text(cropped_person, person_details)

    def __call__(self, person_details: PersonDetails):
        try:
            image = person_details.image
            if image is None:
                raise Exception("Image is None when vision was asked")

            cropped_person = PersonDetectionCropper.detect_and_crop_person(image)
            assert cropped_person is not None

            response = self._describe_person(cropped_person, person_details)

            llm_response = ""
            for chunk in response:
                llm_response += chunk
                yield ApiObject(chunk)
        
            record_assistant_reply(person_details, llm_response)
            RelationshipChecker.adding_text2relationship_checker(person_details)

        except Exception as e:
            raise Exception(f"Exception in the _PersonAttribute {e}")

