import re

class BaseService:
    # Default invalid characters
    invalid_characters = '<>:"|?*'
    max_length = 255  # Default maximum length

    def __init__(self, path: str):
        self.path = path.replace("\\", "/")
        self.path = f"/{self.path}" if not self.path.startswith("/") else self.path
        self.path_length = len(self.path)
        self.path_parts = self.path.strip("/").split('/') if '/' in self.path else [self.path]

    @staticmethod
    def path_part_contains_invalid_characters(part):
        invalid_pattern = re.compile(f"[{re.escape(BaseService.invalid_characters)}]")
        return re.search(invalid_pattern, part)

    def check_path_length(self):
        """Check if the path length exceeds the maximum allowed."""
        if self.path_length > self.max_length:
            raise ValueError(
                f"The specified path is too long. "
                f"Current length: {self.path_length} characters. "
                f"Maximum allowed length is {self.max_length} characters."
            )

    def check_invalid_character(self, part):
        """Check for invalid characters in a part."""
        invalid_character = self.path_part_contains_invalid_characters(part)
        if invalid_character:
            raise ValueError(
                f'Invalid character "{invalid_character.group()}" found in: "{part}". '
                f'Please avoid using: {self.invalid_characters}'
            )

    def check_leading_trailing_spaces(self, part):
        """Check for leading or trailing spaces in a part."""
        if part != part.strip():
            raise ValueError(f'Leading or trailing spaces are not allowed in: "{part}".')

    def check_if_valid_folder(self, part):
        """Perform folder-specific checks."""
        self.check_invalid_character(part)
        self.check_leading_trailing_spaces(part)

    def check_if_valid_filename(self, filename):
        """Perform filename-specific checks."""
        if '.' not in filename:
            raise ValueError(f'Filename "{filename}" must contain an extension.')
        self.check_leading_trailing_spaces(filename)
        self.check_invalid_character(filename)

    def check_if_valid(self):
        """Validate the path parts."""
        self.check_path_length()  # Use the overridden value if in a subclass
        for idx, part in enumerate(self.path_parts):
            if idx < len(self.path_parts) - 1:  # All but the last part are folders
                self.check_if_valid_folder(part)
            else:  # Last part is the filename
                self.check_if_valid_filename(part)

        return True

    def get_cleaned_path(self):
        # str replace any special characters to empty strings
        for char in self.invalid_characters:
            self.path = self.path.replace(char, "")

        # Clean the path parts and handle filename normalization here
        cleaned_parts = []
        for part in self.path_parts:
            cleaned_part = part.strip().strip(".")  # Strip whitespace from each part and any trailing periods
            if '.' in cleaned_part:
                name_part, ext_part = cleaned_part.rsplit('.', 1)
                cleaned_part = f"{name_part.strip()}.{ext_part.strip()}" if ext_part else name_part.strip()
            cleaned_parts.append(cleaned_part)

        path = '/'.join([s for s in cleaned_parts if s])  # Join the cleaned parts
        if not path.startswith("/"):
            path = "/" + path
        return path
