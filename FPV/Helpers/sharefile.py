from FPV.Helpers._base_service import BaseService


class ShareFile(BaseService):
    # Invalid characters specific to ShareFile
    invalid_characters = ':;*?"<>~'

    def __init__(self, path: str, auto_clean=False):
        super().__init__(path, auto_clean=auto_clean)

    def validate(self):
        """Validate the full path for ShareFile, including invalid characters."""
        self.validate_path_length()
        self.validate_invalid_characters()
        
        # Validate each part does not end with a period and has no leading/trailing spaces
        for part in self.path_parts:
            self.validate_if_part_ends_with_period(part)
            self.validate_if_whitespace_around_parts(part)

        self.validate_empty_parts()

    def clean(self, raise_error=True):
        """Clean and return a ShareFile-compliant path; validate if raise_error is True."""
        cleaned_path = self.path
        cleaned_path = self.clean_and_validate_path("path_length", raise_error=raise_error)
        cleaned_path = self.clean_and_validate_path("invalid_characters", raise_error=raise_error)

        # Remove trailing periods and spaces from each part
        cleaned_path_parts = []
        for part in cleaned_path.split("/"):
            part = self.remove_trailing_periods(part)
            part = self.remove_whitespace_around_parts(part)
            if part:
                cleaned_path_parts.append(part)

        cleaned_path = "/".join(cleaned_path_parts).strip("/")
        cleaned_path = f"/{cleaned_path}" if not cleaned_path.startswith("/") else cleaned_path

        # Revalidate cleaned path if needed
        if raise_error:
            cleaned_path_instance = ShareFile(cleaned_path, auto_clean=False)
            cleaned_path_instance.validate()

        return cleaned_path
