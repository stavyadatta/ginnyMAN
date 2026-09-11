from .api_base import ApiBase
from .speaking import _Speaking
from .silent import _Silent
from .person_attr import _PersonAttribute
from .bad_input import _BadInput
from .no_face import _NoFace
from .movement import _CustomMovement, _StandardMovement
from .secondary_channel import _SecondaryChannel
from .pepper_auto import _PepperAuto
from .g1_gesture import _G1Gesture

Speaking = _Speaking()
Silent = _Silent()
PersonAttribute = _PersonAttribute()
BadInput = _BadInput()
NoFace = _NoFace()
CustomMovement = _CustomMovement()
StandardMovement = _StandardMovement()
SecondaryChannel = _SecondaryChannel()
PepperAuto = _PepperAuto()
G1Gesture = _G1Gesture()

api_call: dict[str, ApiBase] = {
    "speak": Speaking,
    "silent": Silent,
    "vision": PersonAttribute,
    "custom movement": CustomMovement,
    "standard movement": StandardMovement,
    "bad input": BadInput,
    "no face": NoFace,
    "object find": SecondaryChannel,
    "person_auto": PepperAuto,
    "g1 wave": G1Gesture,
    "g1 handshake": G1Gesture,
    "g1 high five": G1Gesture,
    "g1 blow kiss left": G1Gesture,
    "g1 blow kiss right": G1Gesture,
    "g1 confirm wave": G1Gesture,
    "g1 confirm handshake": G1Gesture,
    "g1 confirm high five": G1Gesture,
}

__all__ = ["api_call"]
