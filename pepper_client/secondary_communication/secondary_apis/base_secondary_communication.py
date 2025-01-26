import json

class BaseSecondaryCommunication(object):
    def __init__(self):
        pass


    def develop_api_details(self, api_details):
        return {"api_details": api_details}

    def develop_full_details(self, api_name, api_details):
        if isinstance(api_details, dict) and isinstance(api_name, str):
            object_dict = {"api_name": api_name}
            object_dict.update(api_details)
            object_str = json.dumps(object_dict)
            return object_str
        else:
            raise ValueError("The given input {} and {} " \
                "are of type {}" \
                "and {}".format(api_name, api_details, type(api_name), type(api_details)))

    def __call__(self, secondary_details, pepper):
        self.pepper = pepper
        self.stub = pepper.stub
        self.secondary_stub = pepper.secondary_stub 
        
