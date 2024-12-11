from apis import api_call
from utils import PersonDetails

class _Executor():
    def __init__(self):
        pass

    def __call__(self, person_details: PersonDetails):
        state = str(person_details.get_attribute("state"))

        response = api_call[state](person_details)
        return response
