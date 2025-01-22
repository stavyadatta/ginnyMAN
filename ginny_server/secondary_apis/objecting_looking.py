from utils import SecondaryDetails
class ObjectLookup():
    def __init__(self):
        pass
    
    def __call__(self, secondary_details: SecondaryDetails) -> None:
        img = secondary_details.img
        api_detail = secondary_details.api_detail
        object_name = api_detail.get("object_name")
        assert object_name is not None
