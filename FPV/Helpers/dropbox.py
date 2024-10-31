from FPV.Helpers._base import FPV_Base


class FPV_Dropbox(FPV_Base):
    # Dropbox has a maximum path length of 260 characters
    invalid_characters = '<>:"|?*.'
    max_length = 260

    def __init__(self, path: str, auto_clean=False, relative=True):
        super().__init__(path)
        self.auto_clean = auto_clean
        self.relative = relative
        
        # Define restricted names specific to Dropbox
        self.restricted_names = {
            ".lock", "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", 
            "COM6", "COM7", "COM8", "COM9", "LPT1", 
            "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", 
            "LPT7", "LPT8", "LPT9"
        }

        if self.auto_clean:
            self.path = self.clean()

    def validate(self):
        """Validate the full path for Dropbox, including Dropbox-specific validations."""
        self.validate_path_length()
        self.validate_invalid_characters()
        self.validate_restricted_names()

        # Ensure each part has no leading/trailing spaces
        for part in self.path_parts:
            self.validate_if_whitespace_around_parts(part)
        
        self.validate_empty_parts()

    def clean(self, raise_error=True):
        """Clean and return a Dropbox-compliant path; validate if raise_error is True."""
        cleaned_path = self.path
        cleaned_path = self.clean_and_validate_path("path_length", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("invalid_characters", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("restricted_names", path=cleaned_path)
        cleaned_path = self.remove_whitespace_around_parts(cleaned_path)
        cleaned_path = self.remove_empty_parts(cleaned_path)

        # Revalidate if needed
        if raise_error:
            cleaned_path_instance = FPV_Dropbox(cleaned_path)
            cleaned_path_instance.validate()

        return cleaned_path
