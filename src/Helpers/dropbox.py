import re
from Helpers._base_service import BaseService

class Dropbox(BaseService):
    # Invalid characters for Dropbox file and folder names
    invalid_characters = '/\\<>:"|?*'
    max_length = 260

    def __init__(self, path: str):
        # Call the base class constructor
        super().__init__(path)
        
        # Handle filename and extension
        if '.' in self.filename:
            name_part, ext_part = self.filename.rsplit('.', 1)
            self.filename = f"{name_part.strip()}.{ext_part.strip()}" if ext_part else name_part.strip()
        else:
            self.filename = self.filename.strip()

        # Update the last part of path_parts with the cleaned filename
        self.path_parts[-1] = self.filename

    @staticmethod
    def path_part_contains_invalid_characters(part):
        invalid_pattern = re.compile(f"[{re.escape(Dropbox.invalid_characters)}]")
        return re.search(invalid_pattern, part)

    def check_if_valid(self):
        # Path length limitation
        if self.path_length >= self.max_length:
            raise ValueError("Path length must be fewer than 260 characters.")

        # Split the path into parts
        parts = self.path_parts

        # List of restricted names and emojis
        RESTRICTED_NAMES = {
            ".lock", "CON", "PRN", "AUX", "NUL", 
            "COM0", "COM1", "COM2", "COM3", "COM4", 
            "COM5", "COM6", "COM7", "COM8", "COM9", 
            "LPT0", "LPT1", "LPT2", "LPT3", "LPT4", 
            "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        }
        
        # Check each part of the path
        for part in parts:
            # Check for invalid characters
            invalid_character = Dropbox.path_part_contains_invalid_characters(part)
            if invalid_character:
                raise ValueError(
                    f'Invalid character "{invalid_character.group()}" found in "{part}". '
                    f'Please avoid using: {Dropbox.invalid_characters}'
                )

            # Check for emojis or emoticons
            if self.path_part_contains_emoji(part):
                raise ValueError(f'Emojis or emoticons are not allowed in "{part}".')

            # Check for restricted names
            if part in RESTRICTED_NAMES:
                raise ValueError(f'Restricted name found in path: "{part}"')

            # Check for leading or trailing spaces
            if part != part.strip():
                raise ValueError(f'Leading or trailing spaces found in path: "{part}"')

        return True

    def get_cleaned_path(self):
        # Return the cleaned path
        return "/".join([x.strip() for x in self.path_parts if x.strip()])
