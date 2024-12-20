from FPV.Helpers._base import FPV_Base

class FPV_Box(FPV_Base):
    # Box-specific invalid characters and maximum length
    invalid_characters = '<>:"|?*'
    max_length = 255
    restricted_names = {
        "outlook.pst", "quickbooks.qbb", "google_docs.gdoc", 
        "google_sheets.gsheet", "google_slides.gslides", "mac_package.pkg"
    }

    def __init__(self, path: str, **kwargs):
        super().__init__(path, **kwargs)

        if self.auto_clean:
            self.clean()

    def validate(self):
        """Validate the path for Box-specific rules, ignoring OS-specific restrictions."""
        self.process_path_length(action="validate")
        self.process_invalid_characters(action="validate")
        self.process_restricted_names(action="validate")
        self.process_whitespace(action="validate")
        self.process_empty_parts(action="validate")

    def clean(self, raise_error=True):
        """Clean and return a Box-compliant path, validating if raise_error is True."""
        self.process_path_length(action="clean")
        self.process_restricted_names(action="clean")
        self.process_whitespace(action="clean")
        self.process_empty_parts(action="clean")
        self.process_trailing_periods(action="clean")  # Assuming trailing periods logic exists

        if raise_error:
            self.validate()

        return self.get_full_path()
