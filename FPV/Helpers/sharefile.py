from FPV.Helpers._base import FPV_Base


class FPV_ShareFile(FPV_Base):
    # Invalid characters specific to ShareFile
    invalid_characters = ':;*?"<>~'
    max_length = 255  # ShareFile has a maximum path length of 255 characters

    def __init__(self, path: str, auto_clean=False, relative=True, sep="/", check_files=True, check_folders=True):
        super().__init__(path, auto_clean=auto_clean, relative=relative, sep=sep, check_files=check_files, check_folders=check_folders)
        self.auto_clean = auto_clean
        self.relative = relative

        if self.auto_clean:
            self.path = self.clean()

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
        cleaned_path = self.clean_and_validate_path("path_length", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("invalid_characters", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("whitespace_around_parts", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("whitespace_around_parts", path=cleaned_path)

        # Remove trailing periods and spaces from each part
        cleaned_path_parts = []
        for part in cleaned_path.split(self.sep):
            part = self.remove_trailing_periods(part)
            if part:
                cleaned_path_parts.append(part)

        cleaned_path = self.sep.join(cleaned_path_parts).strip(self.sep)
        cleaned_path = f"{self.sep}{cleaned_path}" if not cleaned_path.startswith(self.sep) else cleaned_path

        # Revalidate cleaned path if needed
        if raise_error:
            cleaned_path_instance = FPV_ShareFile(cleaned_path, auto_clean=False)
            cleaned_path_instance.validate()

        return cleaned_path
