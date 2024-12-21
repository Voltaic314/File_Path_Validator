from FPV.Helpers._base import FPV_Base


class FPV_Dropbox(FPV_Base):
    # Dropbox-specific rules
    invalid_characters = '<>:"|?*.'
    max_length = 260
    restricted_names = {
        ".lock", "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", 
        "COM6", "COM7", "COM8", "COM9", "LPT1", 
        "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", 
        "LPT7", "LPT8", "LPT9"
    }
    acceptable_root_patterns = [r"^/$", r"^/root$"]

    def __init__(self, path: str, **kwargs):
        super().__init__(path, **kwargs)

    def validate(self):
        """Validate the path for Dropbox-specific rules."""
        self.process_path_length(action="validate")
        self.process_invalid_characters(action="validate")
        self.process_restricted_names(action="validate")
        self.process_whitespace(action="validate")
        self.process_empty_parts(action="validate")
        return super().validate()

    def clean(self, raise_error=True):
        """Clean and return a Dropbox-compliant path."""
        self.process_path_length(action="clean")
        self.process_invalid_characters(action="clean")
        self.process_restricted_names(action="clean")
        self.process_whitespace(action="clean")
        self.process_empty_parts(action="clean")

        if raise_error:
            self.validate()

        return super().clean()
