from FPV.Helpers._base import FPV_Base

class FPV_Box(FPV_Base):
    # Box-specific invalid characters and maximum length
    invalid_characters = '<>:"|?*'
    max_length = 255
    restricted_names = {
        "outlook.pst", "quickbooks.qbb", "google_docs.gdoc", 
        "google_sheets.gsheet", "google_slides.gslides", "mac_package.pkg"
    }
    acceptable_root_patterns = [
        r"^root$",       # Explicit root folder named "root" (internal representation)
        r"^[^/<>:\"|?*]+$"  # User-facing paths for top-level folders
    ]

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
        return super().validate() # omg babe I feel so validated right now \(>.<)/ <3

    def clean(self, raise_error=True):
        """Clean and return a Box-compliant path, validating if raise_error is True."""
        self.process_path_length(action="clean")
        self.process_restricted_names(action="clean")
        self.process_whitespace(action="clean")
        self.process_empty_parts(action="clean")
        self.process_trailing_periods(action="clean")  

        if raise_error:
            self.validate()

        # so fresh and so clean clean 
        return super().clean() # she's a super clean.. super clean, she's super clean yeah! 
