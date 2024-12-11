from utils import Neo4j

from .api_base import ApiBase

class _Silent(ApiBase):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, person_details):
        response = " "

        for empty in response.split(","):
            yield empty

        Neo4j.add_message_to_person(person_details)
