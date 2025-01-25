from .api_base import ApiBase
from .speaking import _Speaking
from .silent import _Silent
from .person_attr import _PersonAttribute
from .bad_input import _BadInput
from .movement import _Movement
from .api_object import ApiObject
from .secondary_channel import _SecondaryChannel

Speaking = _Speaking()
Silent = _Silent()
PersonAttribute = _PersonAttribute()
BadInput = _BadInput()
Movement = _Movement()
SecondaryChannel = _SecondaryChannel()

api_call: dict[str, ApiBase] = {
    "speak": Speaking,
    "silent": Silent,
    "vision": PersonAttribute,
    "movement": Movement,
    "bad input": BadInput,
    "object find": SecondaryChannel
}

__all__ = ["api_call", "ApiObject"]
