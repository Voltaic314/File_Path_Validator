class Path:
    """ Helper class to manage and manipulate paths dynamically. """
    def __init__(self, initial_path: str = "", sep: str = "/"):
        """
        Initialize the path helper.

        :param initial_path: Initial path to populate the stack.
        :param sep: Path separator, defaults to '/'.
        """
        self.parts = initial_path.split(sep) if initial_path else []
        self.sep = sep

    def add(self, part: str, mode: str = "validate", clean_func=None, validate_func=None):
        """
        Add a new part to the path.

        :param part: Path part to add.
        :param mode: Mode ('clean', 'validate', or 'None') to process the part.
        :param clean_func: Function to clean the part.
        :param validate_func: Function to validate the part.
        """
        if mode == "clean" and clean_func:
            part, _ = clean_func(part)
        if mode == "validate" and validate_func:
            validate_func(part)
        self.parts.append(part)

    def remove(self, index: int = -1):
        """
        Remove a part of the path by index (default removes the last part).

        :param index: Index of the part to remove.
        :return: Removed path part.
        """
        if self.parts:
            return self.parts.pop(index)
        raise IndexError("Cannot remove from an empty path.")

    def set(self, index: int, part: str, mode: str = "validate", clean_func=None, validate_func=None):
        """
        Replace a part of the path at a specific index.

        :param index: Index of the path part to replace.
        :param part: New path part.
        :param mode: Mode ('clean', 'validate', or 'None') to process the part.
        :param clean_func: Function to clean the part.
        :param validate_func: Function to validate the part.
        """
        if 0 <= index < len(self.parts):
            if mode == "clean" and clean_func:
                part, _ = clean_func(part)
            if mode == "validate" and validate_func:
                validate_func(part)
            self.parts[index] = part
        else:
            raise IndexError("Invalid index for path modification.")

    def get_full_path(self):
        """
        Return the full path as a string.
        """
        return self.sep.join(self.parts)

    def __repr__(self):
        return self.get_full_path()
