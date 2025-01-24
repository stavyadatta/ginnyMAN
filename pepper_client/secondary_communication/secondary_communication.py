import json
from .secondary_apis import secondary_pepper_apis_kit

class _SecondaryCommunication():
    def __init__(self):
        pass

    def __call__(self, text_chunk, mode, pepper):
        text_chunk = json.loads(text_chunk)
        api_name = text_chunk.get("api_name")
        api_details = text_chunk.get("api_details")
        return secondary_pepper_apis_kit[api_name](api_details, pepper)
        
