from .api_base import ApiBase
from .speaking import _Speaking
from .silent import _Silent

Speaking = _Speaking()
Silent = _Silent()

api_call: dict[str, ApiBase] = {
    "speak": Speaking,
    "silent": Silent
}

__all__ = ["api_call"]
