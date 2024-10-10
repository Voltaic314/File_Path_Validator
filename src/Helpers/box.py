import re
from Helpers._base_service import BaseService

class Box(BaseService):
    # Invalid characters for Box file and folder names
    invalid_characters = '<>:"/\\|?*'

    def __init__(self, path: str):
        # Call the base class constructor
        super().__init__(path)
        
        # Store the original path
        self.original_path = path
        
        # Automatically strip leading/trailing spaces from the entire path and each component
        self.path = '/'.join(s.strip() for s in self.path.strip('/').split('/'))
        
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
        invalid_pattern = re.compile(f"[{re.escape(Box.invalid_characters)}]")
        return re.search(invalid_pattern, part)

    def check_if_valid(self):
        # Split the path into parts
        parts = self.path_parts

        # Check each part of the path
        for idx, part in enumerate(parts):
            is_folder = idx < len(parts) - 1  # Last part is typically the filename

            # Check for invalid characters
            invalid_character = Box.path_part_contains_invalid_characters(part)
            if invalid_character:
                raise ValueError(
                    f'Invalid character "{invalid_character.group()}" found in "{part}". '
                    f'Please avoid using: {Box.invalid_characters}'
                )

            # Check for leading or trailing whitespaces
            if part != part.strip():
                raise ValueError(f'Leading or trailing whitespaces are not allowed in "{part}".')

            # Check for leading spaces (Mac OS restriction)
            if part.startswith(' '):
                raise ValueError(f'Leading spaces are not allowed in "{part}".')

            # Windows restriction: Folder names cannot end with a period '.'
            if is_folder and part.endswith('.'):
                raise ValueError(f'Folder names cannot end with a period "." in "{part}".')

            # Box OS-independent restriction: '/' and '\' are not allowed anywhere in a file or folder name
            if '/' in part or '\\' in part:
                raise ValueError(f'Slashes "/" or "\\" are not allowed in "{part}".')

        return True

    def get_cleaned_path(self):
        # Return the cleaned path
        path = '/'.join([s.strip() for s in self.path_parts if s.strip()])
        if not path.startswith("/"):
            path = "/" + path
        return path
