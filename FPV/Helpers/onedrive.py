import re
from FPV.Helpers._base_service import BaseService

class OneDrive(BaseService):
    # Invalid characters for OneDrive file and folder names
    invalid_characters = '<>:"/\\|?*#'

    def __init__(self, path: str, windows_sync: bool = True):
        super().__init__(path)
        
        # Store the original path
        self.original_path = path
        
        # Handle filename and extension
        self.filename = self.path_parts[-1] if self.path_parts else self.path
        self.filename_ext = self.filename.split('.')[-1]

        # Set maximum path length based on the sync option
        self.max_length = 255 if windows_sync else 400

    @staticmethod
    def path_part_contains_invalid_characters(part):
        invalid_pattern = re.compile(f"[{re.escape(OneDrive.invalid_characters)}]")
        return re.search(invalid_pattern, part)

    def check_if_valid(self):
        # Check length limitations
        if self.path_length > self.max_length:
            raise ValueError(
                f"The specified path is too long. "
                f"Current length: {self.path_length} characters. "
                f"Maximum allowed length is {self.max_length} characters."
            )

        # List of restricted names and prefixes
        RESTRICTED_NAMES = {
            ".lock", "CON", "PRN", "AUX", "NUL", 
            "COM0", "COM1", "COM2", "COM3", "COM4", 
            "COM5", "COM6", "COM7", "COM8", "COM9", 
            "LPT0", "LPT1", "LPT2", "LPT3", "LPT4", 
            "LPT5", "LPT6", "LPT7", "LPT8", "LPT9", 
            "_vti_", "desktop.ini"
        }
        RESTRICTED_PREFIX = "~$"
        RESTRICTED_ROOT_LEVEL_FOLDER = "forms"

        # Check each part of the path
        for part in self.path_parts:
            # Check for invalid characters
            invalid_character = OneDrive.path_part_contains_invalid_characters(part)
            if invalid_character:
                raise ValueError(
                    f"Invalid character \"{invalid_character.group()}\" found in this section of the proposed file path: \"{part}\". "
                    f"Please make sure the file path does not contain any of the following characters: {OneDrive.invalid_characters}"
                )
            
            # Check for restricted names
            if part in RESTRICTED_NAMES:
                raise ValueError(f"Restricted name found in path: \"{part}\"")
            
            # Check for leading or trailing spaces
            if part != part.strip():
                raise ValueError(f"Leading or trailing spaces found in path: \"{part}\"")
            
            # Check for restricted prefixes
            if part.startswith(RESTRICTED_PREFIX):
                raise ValueError(f"Restricted prefix found in path: \"{part}\"")
            
            # Check for restricted root level folder name
            if part.lower() == RESTRICTED_ROOT_LEVEL_FOLDER and self.path_parts.index(part) == 0:
                raise ValueError(f"Restricted root level folder name found in path: \"{part}\". Please make sure the first part of the path is not \"{RESTRICTED_ROOT_LEVEL_FOLDER}\"")
        
        return True
    
    def get_cleaned_path(self):
        return '/'.join([s.strip() for s in self.path_parts if s.strip()])
