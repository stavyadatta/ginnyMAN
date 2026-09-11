from .standard_prompt import movement_prompt as STANDARD_MOVEMENT_PROMPT
from .movement_base import _MovementApi


class _StandardMovement(_MovementApi):
    movement_prompt = STANDARD_MOVEMENT_PROMPT
    response_mode = 'standard_movement'
