from .api_base import ApiBase
from .speaking import _Speaking
from .silent import _Silent
from .person_attr import _PersonAttribute
from .bad_input import _BadInput

Speaking = _Speaking()
Silent = _Silent()
PersonAttribute = _PersonAttribute()
BadInput = _BadInput()

api_call: dict[str, ApiBase] = {
    "speak": Speaking,
    "silent": Silent,
    "vision": PersonAttribute,
    "bad input": BadInput
}

__all__ = ["api_call"]
