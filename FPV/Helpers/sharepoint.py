import re
from FPV.Helpers._base_service import BaseService

class SharePoint(BaseService):
    # Invalid characters for SharePoint file and folder names
    invalid_characters = BaseService.invalid_characters + "#"
    
    def __init__(self, path: str, windows_sync: bool = True):
        super().__init__(path)  # Call the base class constructor

        # Set maximum path length based on the sync option
        self.max_length = 255 if windows_sync else 400

    def check_if_valid(self):
        # Call the base class check for path length and general validation
        super().check_if_valid()  

        # List of restricted names for SharePoint
        self.RESTRICTED_NAMES = {
            ".lock", "CON", "PRN", "AUX", "NUL", 
            "COM0", "COM1", "COM2", "COM3", "COM4", 
            "COM5", "COM6", "COM7", "COM8", "COM9", 
            "LPT0", "LPT1", "LPT2", "LPT3", "LPT4", 
            "LPT5", "LPT6", "LPT7", "LPT8", "LPT9", 
            "_vti_", "desktop.ini"
        }
        self.RESTRICTED_PREFIX = "~$"
        self.RESTRICTED_ROOT_LEVEL_FOLDER = "forms"

        # Check each part of the path
        for part in self.path_parts:
            # Check for invalid characters
            invalid_character = SharePoint.path_part_contains_invalid_characters(part)
            if invalid_character:
                raise ValueError(
                    f'Invalid character "{invalid_character.group()}" found in this section of the proposed file path: "{part}". '
                    f'Please make sure the file path does not contain any of the following characters: {SharePoint.invalid_characters}'
                )
            
            # Check for restricted names
            if part in self.RESTRICTED_NAMES:
                raise ValueError(f'Restricted name found in path: "{part}"')
            
            # Check for restricted prefixes
            if part.startswith(self.RESTRICTED_PREFIX):
                raise ValueError(f'Restricted prefix found in path: "{part}"')
            
            # Check for restricted root level folder name
            if part.lower() == self.RESTRICTED_ROOT_LEVEL_FOLDER and self.path_parts.index(part) == 0:
                raise ValueError(f'Restricted root level folder name found in path: "{part}". Please make sure the first part of the path is not "{RESTRICTED_ROOT_LEVEL_FOLDER}"')

        return True

    def get_cleaned_path(self, raise_error: bool = True):
        cleaned_path = super().get_cleaned_path(raise_error)
        
        cleaned_path_parts = []
        for index, part in enumerate(cleaned_path.split("/")):

            for restricted_name in self.RESTRICTED_NAMES:
                part = part.replace(restricted_name, "")

            part = part.replace(self.RESTRICTED_PREFIX, "")

            part = part.strip().rstrip(".")

            if index == 0:
                part = part.replace(self.RESTRICTED_ROOT_LEVEL_FOLDER, "")
                
            if not part:
                continue
            
            cleaned_path_parts.append(part)
        
        output_path = '/'.join(cleaned_path_parts)
        output_path = output_path.strip('/')
        output_path = f'{"/" + output_path}' if not output_path.startswith("/") else output_path

        cleaned_path_instance = SharePoint(output_path)
        if raise_error:
            cleaned_path_instance.check_if_valid()
        
        return cleaned_path_instance.path