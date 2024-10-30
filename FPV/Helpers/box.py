from FPV.Helpers._base_service import BaseService


class Box(BaseService):
    # Box-specific invalid characters and maximum length
    invalid_characters = ''
    max_length = 255

    def __init__(self, path: str, auto_clean=False, relative=True):
        super().__init__(path, auto_clean=auto_clean, relative=relative)
        
        # Box-specific restricted names or unsupported file types
        self.restricted_names = {
            "outlook.pst", "quickbooks.qbb", "google_docs.gdoc", 
            "google_sheets.gsheet", "google_slides.gslides", "mac_package.pkg"
        }
    def validate(self):
        """Validate the path for Box-specific rules, ignoring OS-specific restrictions."""
        self.validate_path_length()
        self.validate_invalid_characters()
        self.validate_restricted_names()

        # Validate each part for leading/trailing whitespace
        for part in self.path_parts:
            self.validate_if_whitespace_around_parts(part)

        self.validate_empty_parts()

    def clean(self, raise_error=True):
        """Clean and return a Box-compliant path, validating if raise_error is True."""
        cleaned_path = self.path
        cleaned_path = self.clean_and_validate_path("path_length", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("restricted_names", path=cleaned_path)

        # Clean each part for whitespace and restricted characters
        cleaned_path_parts = []
        for part in cleaned_path.split('/'):
            part = self.remove_whitespace_around_parts(part)
            part = part.strip().rstrip(".")

            if part:
                cleaned_path_parts.append(part)

        cleaned_path = '/'.join(cleaned_path_parts).strip('/')
        cleaned_path = f"/{cleaned_path}" if not cleaned_path.startswith("/") else cleaned_path

        if raise_error:
            cleaned_path_instance = Box(cleaned_path, auto_clean=False, relative=self.relative)
            cleaned_path_instance.validate()

        return cleaned_path
