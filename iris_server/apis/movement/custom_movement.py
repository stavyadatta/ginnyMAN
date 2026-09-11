from .custom_prompt import movement_prompt as CUSTOM_MOVEMENT_PROMPT
from .movement_base import _MovementApi


class _CustomMovement(_MovementApi):
    movement_prompt = CUSTOM_MOVEMENT_PROMPT
    response_mode = 'custom_movement'
