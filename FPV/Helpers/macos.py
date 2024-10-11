import re
from FPV.Helpers._base_service import BaseService

class MacOS(BaseService):
    # Invalid characters for macOS file and folder names
    invalid_characters = r'<>:"/\\|?*'

    def __init__(self, path: str):
        super().__init__(path)
        
        # Handle filename and extension
        self.filename = self.path_parts[-1] if self.path_parts else self.path
        if '.' in self.filename:
            name_part, ext_part = self.filename.rsplit('.', 1)
            self.filename = f"{name_part.strip()}.{ext_part.strip()}" if ext_part else name_part.strip()
        else:
            self.filename = self.filename.strip()

        # Update the last part of path_parts with the cleaned filename
        self.path_parts[-1] = self.filename

    @staticmethod
    def path_part_contains_invalid_characters(part):
        invalid_pattern = re.compile(f"[{re.escape(MacOS.invalid_characters)}]")
        return re.search(invalid_pattern, part)

    def check_if_valid(self):
        # Path length limitation
        if self.path_length > 255:
            raise ValueError(
                f"The specified path is too long. "
                f"Current length: {self.path_length} characters. "
                f"Maximum allowed length is 255 characters."
            )

        # Split the path into parts
        parts = self.path_parts

        # Check each part of the path
        for idx, part in enumerate(parts):
            is_last_part = (idx == len(parts) - 1)
            is_folder = not is_last_part

            # Check for empty names or names that are just spaces
            if not part or part.strip() == '':
                raise ValueError("File or folder names cannot be empty or just spaces.")

            # Check for invalid characters
            invalid_character = MacOS.path_part_contains_invalid_characters(part)
            if invalid_character:
                raise ValueError(
                    f'Invalid character "{invalid_character.group()}" found in "{part}". '
                    f'Please avoid using: {MacOS.invalid_characters}'
                )

            # Check for leading or trailing whitespaces
            if part != part.strip():
                raise ValueError(f'Leading or trailing whitespaces are not allowed in "{part}".')

            # Check for filenames ending with a period without an extension
            if is_last_part:  # Filename
                if part.endswith('.') and '.' not in part[:-1]:
                    raise ValueError('A filename cannot end with a period without an extension.')
            else:
                # For folders, disallow names ending with a period
                if part.endswith('.'):
                    raise ValueError('Folder names cannot end with a period.')

        return True

    def get_cleaned_path(self):
        # Return the cleaned path
        return '/'.join([s.strip() for s in self.path_parts if s.strip()])
