from .api_base import ApiBase
from .speaking import _Speaking
from .silent import _Silent
from .person_attr import _PersonAttribute

Speaking = _Speaking()
Silent = _Silent()
PersonAttribute = _PersonAttribute()

api_call: dict[str, ApiBase] = {
    "speak": Speaking,
    "silent": Silent,
    "vision": PersonAttribute
}

__all__ = ["api_call"]
