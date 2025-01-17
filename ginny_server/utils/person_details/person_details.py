class PersonDetails:
    def __init__(self, person_dict: dict={}) -> None:
        self.person_dict = person_dict
        self.image = None

    def __bool__(self):
        return bool(self.person_dict)

    def get_person(self):
        if self.person_dict:
            return self.person_dict
        else:
            raise Exception("The person object is empty")

    def get_attribute(self, field: str):
        return self.person_dict.get(field, [])

    def set_attribute(self, update_field: str, update_string: str):
        """
            The function updates the person details within the object

            :param update_field: The field or the key that needs to be updated
            :param update_string: The string that will be used to update the dictionary
        """
        if self.person_dict:
            self.person_dict[update_field] = update_string
        else:
            raise Exception("The person object is empty")

    def add_message(self, additional_message: dict):
        """
            The message that needs to be added to the person details dictionary item

            :param additional_message: The message that needs to be added to the 
        """
        if self.person_dict:
            self.person_dict["messages"].append(additional_message)
        else:
            raise Exception("Detail of the person is not found, nothing to add")

    def set_image(self, image):
        self.image = image
