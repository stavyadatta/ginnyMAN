from utils import Neo4j, PersonDetails, ApiObject
from .api_base import ApiBase

class _Reset(ApiBase):
    def __init__(self):
        super().__init__()

    def __call__(self, person_details: PersonDetails):
        face_id = person_details.get_attribute("face_id")
        Neo4j.reset_person_message(face_id)

        response = "reset the game"

        yield ApiObject(response)



