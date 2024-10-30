import re


class BaseService:
    """Base class for path validation and cleaning."""
    # Default invalid characters
    invalid_characters = ''
    max_length = 0  # Default maximum length

    corresponding_validate_and_clean_methods  = {
        "path_length": {"validate": "validate_path_length", "clean": "truncate_path"},
        "restricted_names": {"validate": "validate_restricted_names", "clean": "remove_restricted_names"},
        "part_ends_with_period": {"validate": "validate_if_part_ends_with_period", "clean": "remove_trailing_periods"},
        "whitespace_around_parts": {"validate": "validate_if_whitespace_around_parts", "clean": "remove_whitespace_around_parts"},
        "empty_parts": {"validate": "validate_empty_parts", "clean": "remove_empty_parts"},
        "invalid_characters": {"validate": "validate_invalid_characters", "clean": "remove_invalid_characters"},
        "_main": {"validate": "validate", "clean": "clean"}
    }

    def __init__(self, path: str, auto_clean: bool = False, relative: bool = True):
        self.original_path = path
        self.path = path.replace("\\", "/")
        self.path_parts = self.path.strip("/").split('/') if '/' in self.path else [self.path]
        self.path = f"/{self.path}" if not self.path.startswith("/") else self.path
        self.restricted_names = set()
        self.relative = relative

        if auto_clean:
            self.path = self.clean()

    def get_validate_or_clean_method(self, method: str, action: str, **kwargs):
        """
        The purpose of this method is to return the appropriate 
        validate or clean method based on the method and action passed.
        If you pass in "clean" as your action argument then you need to also pass in the "path" argument.

        Args:
            method (str): The name of the validate/clean method pair to use.
            action (str): The action to perform, either "validate" or "clean".
            **kwargs: Additional keyword arguments to pass to the method.

        Returns:
        if action == "validate":
            bool: The result of the validation.
        elif action == "clean":
            str: The cleaned path.
        """
        return getattr(self, self.corresponding_validate_and_clean_methods[method][action], **kwargs)
    
    def clean_and_validate_path(self, method: str, raise_error: bool = False, path: str = '', **kwargs):
        """
        Clean the path with the specified clean method, then optionally validate.
        
        Args:
            method (str): The name of the validate/clean method pair to use.
            raise_error (bool): Whether to raise an error if the cleaned path is still invalid.

        Returns:
            str: The cleaned path.
        """
        # Call the clean method
        clean_method = self.get_validate_or_clean_method(method, "clean")
        cleaned_path = clean_method(path if path else self.path, **kwargs)

        # If raise_error is set, validate the cleaned path
        if raise_error:
            # Create a new instance of the current class with the cleaned path
            cleaned_instance = self.__class__(cleaned_path, **kwargs)
            validate_method = self.get_validate_or_clean_method(method, "validate")
            cleaned_instance.validate()

        return cleaned_path

    def path_part_contains_invalid_characters(self, part):
        invalid_pattern = re.compile(f"[{re.escape(self.invalid_characters)}]")
        return re.search(invalid_pattern, part)

    def validate_invalid_characters(self):
        """Validate for invalid characters in each part of the path and report specific invalid characters."""
        for part in self.path_parts:
            match = self.path_part_contains_invalid_characters(part)
            if match:
                raise ValueError(
                    f'Invalid character "{match.group()}" found in part: "{part}". '
                    f'Please ensure the path does not contain any of the following characters: {self.invalid_characters}'
                )

    def remove_invalid_characters(self, path):
        """Remove invalid characters from each part of the path and return the cleaned path."""
        cleaned_parts = []
        for part in path.strip("/").split('/'):
            cleaned_part = re.sub(f"[{re.escape(self.invalid_characters)}]", "", part)
            if cleaned_part:  # Only add non-empty parts
                cleaned_parts.append(cleaned_part)
        return "/".join(cleaned_parts)

    def validate_path_length(self):
        """validate if the path length exceeds the maximum allowed."""
        if self.max_length and len(self.path) > self.max_length:
            raise ValueError(f"The specified path is too long. Maximum allowed is {self.max_length} characters.")

    def truncate_path(self, path):
        """Truncate the path length to meet the maximum length requirement."""
        if len(path) <= self.max_length:
            return path
        
        # Use as much of the filename as possible but raise if the filename alone exceeds max length
        filename = path.split('/')[-1]
        filename_length = len(filename)
        if filename_length > self.max_length:
            raise ValueError(f"The filename is too long. Maximum allowed is {self.max_length} characters.")

        # Calculate maximum usable path length minus filename
        max_path_length = self.max_length - filename_length - 1
        truncated_path = path[:max_path_length]
        
        return f"/{truncated_path.strip('/')}/{filename.strip('/')}"

    def validate_restricted_names(self):
        """validate for restricted names in each part of the path."""
        for part in self.path_parts:
            if part.lower() in [s.lower() for s in self.restricted_names]:
                raise ValueError(f'Restricted name "{part}" found in path.')

    def remove_restricted_names(self, path):
        """Remove restricted names from each part of the path and return the cleaned path."""
        cleaned_parts = [part for part in path.strip("/").split('/') if part not in self.restricted_names]
        return "/".join(cleaned_parts)

    def validate_if_part_ends_with_period(self):
        """validate if any part of the path ends with a period."""
        for part in self.path_parts:
            if part.endswith('.'):
                raise ValueError(f'"{part}" cannot end with a period.')

    def remove_trailing_periods(self, path):
        """Remove trailing periods from each part of the path and return the cleaned path."""
        cleaned_parts = [part.rstrip('.') for part in path.strip("/").split('/') if part.rstrip('.')]
        return "/".join(cleaned_parts)

    def validate_if_whitespace_around_parts(self):
        """validate if there are leading or trailing spaces in any part of the path."""
        for part in self.path_parts:
            if part != part.strip():
                raise ValueError(f'Leading or trailing spaces are not allowed in: "{part}".')

    def remove_whitespace_around_parts(self, path):
        """Remove leading and trailing spaces from each part of the path and return the cleaned path."""
        cleaned_parts = [part.strip() for part in path.strip("/").split('/') if part.strip()]
        return "/".join(cleaned_parts)

    def validate_empty_parts(self):
        """validate for empty parts in the path."""
        if '' in self.path_parts:
            raise ValueError('Empty parts are not allowed in the path.')

    def remove_empty_parts(self, path):
        """Remove any empty parts in the path and return the cleaned path."""
        cleaned_parts = [part for part in path.strip("/").split('/') if part]
        return "/".join(cleaned_parts)

    def validate(self):
        return True

    def clean(self, raise_error=True):
        return self.path
