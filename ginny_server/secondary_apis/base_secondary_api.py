from apis import ApiObject
from utils import SecondaryDetails

class BaseSecondaryApi():
    def __init__(self):
        pass
    
    def __call__(self, secondary_details: SecondaryDetails) -> ApiObject:
        return ApiObject()
