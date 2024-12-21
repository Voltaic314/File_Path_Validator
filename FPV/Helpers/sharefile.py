from FPV.Helpers._base import FPV_Base


class FPV_ShareFile(FPV_Base):
    # Invalid characters specific to ShareFile
    invalid_characters = ':;*?"<>~'
    max_length = 255  # ShareFile has a maximum path length of 255 characters
    acceptable_root_patterns = [r"^/$"]

    def __init__(self, path: str, **kwargs):
        super().__init__(path, **kwargs)

    def validate(self):
        """Validate the path for ShareFile-specific rules."""
        self.process_path_length(action="validate")
        self.process_invalid_characters(action="validate")
        self.process_whitespace(action="validate")
        self.process_trailing_periods(action="validate")
        self.process_empty_parts(action="validate")
        super().validate()

    def clean(self, raise_error=True):
        """Clean the path to be ShareFile-compliant and validate if `raise_error` is True."""
        self.process_path_length(action="clean")
        self.process_invalid_characters(action="clean")
        self.process_whitespace(action="clean")
        self.process_trailing_periods(action="clean")
        self.process_empty_parts(action="clean")
        if raise_error:
            self.validate()
        return super().clean()
