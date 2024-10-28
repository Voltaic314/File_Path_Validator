import re
from FPV.Helpers._base_service import BaseService

class OneDrive(BaseService):
    # Set maximum path length for OneDrive
    max_length = 255  # Default for Windows sync, can be overridden if needed

    def __init__(self, path: str, windows_sync: bool = True):
        super().__init__(path)  # Call the base class constructor
        # Set maximum path length based on the sync option
        self.max_length = 255 if windows_sync else 400

    def check_if_valid(self):
        # Call the base class check for path length and general validation
        super().check_if_valid()  

        # List of restricted names for OneDrive
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

        # Check each part of the path for OneDrive specific restrictions
        for part in self.path_parts:
            
            # Check for restricted names
            if part in self.RESTRICTED_NAMES:
                raise ValueError(f'Restricted name found in path: "{part}"')
            
            # Check for leading or trailing spaces
            if part != part.strip():
                raise ValueError(f'Leading or trailing spaces found in path: "{part}"')
            
            # Check for restricted prefixes
            if part.startswith(self.RESTRICTED_PREFIX):
                raise ValueError(f'Restricted prefix found in path: "{part}"')
            
            # Check for restricted root level folder name
            if part.lower() == self.RESTRICTED_ROOT_LEVEL_FOLDER and self.path_parts.index(part) == 0:
                raise ValueError(f'Restricted root level folder name found in path: "{part}". Please make sure the first part of the path is not "{self.RESTRICTED_ROOT_LEVEL_FOLDER}"')

        return True
    
    def get_cleaned_path(self, raise_error: bool = True):
        cleaned_path = super().get_cleaned_path(raise_error)
        
        cleaned_path_parts = []
        # Check for restricted prefixes
        for index, part in enumerate(cleaned_path.split("/")):

            # Remove restricted names
            for restricted_name in self.RESTRICTED_NAMES:
                part = part.replace(restricted_name, "")  

            # strip whitespace and dots
            part = part.strip().rstrip(".")

            # Remove restricted prefixes
            for restricted_prefix in self.RESTRICTED_PREFIX:
                part = part.replace(restricted_prefix, "")
            
            if index == 0 and part.lower() == self.RESTRICTED_ROOT_LEVEL_FOLDER:
                part = part.replace(part, "")
            
            if part:
                cleaned_path_parts.append(part)

        output_path = "/".join(cleaned_path_parts)
        output_path = output_path.strip("/")
        output_path = f'{"/" + output_path}' if not output_path.startswith("/") else output_path

        cleaned_path_instance = OneDrive(output_path)
        if raise_error:
            cleaned_path_instance.check_if_valid()
        
        return cleaned_path_instance.path
