from FPV.Helpers._base import FPV_Base


class FPV_Box(FPV_Base):
    # Box-specific invalid characters and maximum length
    invalid_characters = '<>:"|?*'
    max_length = 255

    def __init__(self, path: str, auto_clean=False, relative=True, sep="/", check_files=True, check_folders=True):
        super().__init__(path, relative=relative, sep=sep, check_files=check_files, check_folders=check_folders)
        self.auto_clean = auto_clean
        self.relative = relative
        
        # Box-specific restricted names or unsupported file types
        self.restricted_names = {
            "outlook.pst", "quickbooks.qbb", "google_docs.gdoc", 
            "google_sheets.gsheet", "google_slides.gslides", "mac_package.pkg"
        }

        if self.auto_clean:
            self.path = self.clean()
    
    def validate(self):
        """Validate the path for Box-specific rules, ignoring OS-specific restrictions."""
        self.validate_path_length()
        self.validate_invalid_characters()
        self.validate_restricted_names()

        # Validate each part for leading/trailing whitespace
        self.validate_if_whitespace_around_parts()
        self.validate_empty_parts()

    def clean(self, raise_error=True, check_files=True):
        """Clean and return a Box-compliant path, validating if raise_error is True."""
        cleaned_path = self.path
        cleaned_path = self.clean_and_validate_path("path_length", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("restricted_names", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("whitespace_around_parts", path=cleaned_path)


        # Clean each part for whitespace and restricted characters
        cleaned_path_parts = []
        path_parts = cleaned_path.split(self.sep)
        for part in path_parts:
            part = self.remove_trailing_periods(part)

            if part:
                cleaned_path_parts.append(part)
        
        cleaned_path = self.sep.join(cleaned_path_parts)

        cleaned_path = self.sep.join(cleaned_path_parts).strip(self.sep)
        cleaned_path = f"{self.sep}{cleaned_path}" if not cleaned_path.startswith(self.sep) else cleaned_path

        if raise_error:
            cleaned_path_instance = FPV_Box(cleaned_path, auto_clean=False, relative=self.relative)
            cleaned_path_instance.validate()

        return cleaned_path
