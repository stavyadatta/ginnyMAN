class ApiObject:
    def __init__(self, textchunk=None, movement='default', code=None):
        """
        Initialize the ApiObject class.

        Parameters:
        movement: Optional. Represents movement data.
        textchunk: Optional. Represents a chunk of text.
        code: Optional. Represents code data.
        """
        self.movement = movement
        self.textchunk = textchunk
        self.code = code

    def __repr__(self):
        """
        String representation of the ApiObject.
        """
        return f"ApiObject(movement={self.movement}, textchunk={self.textchunk}, code={self.code})"
