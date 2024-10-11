from FPV.Helpers._base_service import BaseService


class OSBase(BaseService):
    def __init__(self, path: str, service: str):
        super().__init__(path)  # Call BaseService initializer
        self.service = service.lower()

    def check_if_valid(self):
        if self.service == "windows":
            return Windows(self.path).check_if_valid()
        elif self.service == "mac_os":
            return MacOS(self.path).check_if_valid()
        elif self.service == "linux":
            return Linux(self.path).check_if_valid()
        else:
            raise ValueError(f"Unsupported OS service: {self.service}")


class Windows(OSBase):

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


class MacOS(OSBase):
    # mac os doesn't have any invalid characters other than 
    # the obvious path delimiter but we're already handling that 
    # in the base class. :) 
    invalid_characters = '' 

    def __init__(self, path: str):
        super().__init__(path)

    def check_if_valid(self):
        super().check_if_valid()  # Call base validation first

        # Check for reserved file names (not explicitly required, but avoid common issues)
        RESTRICTED_NAMES = {
            ".DS_Store", "Icon\\r", "Thumbs.db"
        }

        if self.filename in RESTRICTED_NAMES:
            raise ValueError(f'Reserved name "{self.filename}" is not allowed.')

        return True


class Linux(OSBase):
    invalid_characters = '\0'  # Only null character is invalid in Linux

    def __init__(self, path: str):
        super().__init__(path)

    def check_if_valid(self):
        super().check_if_valid()  # Call base validation first

        # Linux-specific checks can go here if needed

        return True
