from .base_secondary_communication import BaseSecondaryCommunication
from .finding_object import _ObjectLookup

ObjectLookup = _ObjectLookup()

secondary_pepper_apis_kit = {
    "ObjectLookup": ObjectLookup
}

__all__ = ["secondary_pepper_apis_kit"]
