from FPV.Helpers._base_service import BaseService


class Windows(BaseService):
    def check_if_valid(self):
        """Check validity of the full path for Windows, including base checks and Windows-specific checks."""
        super().check_if_valid()  # Calls the base validation logic

        # Check for reserved names in Windows
        reserved_names = {
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        }
        for part in self.path_parts:
            if part.upper() in reserved_names:
                raise ValueError(f'Reserved name "{part}" is not allowed in Windows.')
            
    def get_cleaned_path(self, raise_error: bool = True):
        cleaned_path = super().get_cleaned_path(raise_error)


class MacOS(BaseService):
    # mac os doesn't have any invalid characters other than 
    # the obvious path delimiter but we're already handling that 
    # in the base class. 
    invalid_characters = '' 

    def check_if_valid(self):
        super().check_if_valid()  # Call base validation first

        # Check for reserved file names (not explicitly required, but avoid common issues)
        RESTRICTED_NAMES = {
            ".DS_Store",
            "._myfile"
        }

        if self.filename in RESTRICTED_NAMES:
            raise ValueError(f'Reserved name "{self.filename}" is not allowed.')

        return True


class Linux(BaseService):
    invalid_characters = '\0'  # Only null character is invalid in Linux

    def check_if_valid(self):
        super().check_if_valid()  # Call base validation first

        # Linux-specific checks can go here if needed

        return True
