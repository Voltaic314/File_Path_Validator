import re
from FPV.Helpers._base_service import BaseService


class Windows(BaseService):
    invalid_characters = '<>:"|?*'
    max_length = 255

    def __init__(self, path, auto_clean=False, relative=True):
        super().__init__(path, auto_clean=auto_clean, relative=relative)
        if not relative:
            if self.path.startswith("/"):
                self.path = self.path[1:] # this should fix any weird "/C:/" paths due to the base formatting it does :) 
        self.restricted_names = {
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", 
            "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", 
            "LPT6", "LPT7", "LPT8", "LPT9"
        }

    def validate(self):
        """Validate the full path for Windows, including Windows-specific validations."""
        if not self.relative:
            self.validate_drive_letter()
        
        self.validate_path_length()
        self.validate_invalid_characters()
        self.validate_restricted_names()
        
        # Validate each part does not end with a period and has no leading/trailing spaces
        for part in self.path_parts:
            self.validate_if_part_ends_with_period(part)
            self.validate_if_whitespace_around_parts(part)

        self.validate_empty_parts()

    def clean(self, raise_error=True):
        """Clean and return the Windows-compliant path, and validate if raise_error is True."""
        cleaned_path = self.path
        cleaned_path = self.clean_and_validate_path("path_length", raise_error=raise_error)
        cleaned_path = self.clean_and_validate_path("invalid_characters", raise_error=raise_error)
        cleaned_path = self.clean_and_validate_path("restricted_names", raise_error=raise_error)
        
        # Remove trailing periods and spaces
        for part in self.path_parts:
            cleaned_path = self.remove_trailing_periods(part)
            cleaned_path = self.remove_whitespace_around_parts(part)

        cleaned_path = self.remove_empty_parts(cleaned_path)

        # Validate cleaned path if needed
        if raise_error:
            cleaned_path_instance = Windows(cleaned_path)
            cleaned_path_instance.validate()

        return cleaned_path

    def validate_drive_letter(self):
        """Verify that the path starts with a valid drive letter (Windows-specific)."""
        drive_letter_pattern = re.compile(r"^[A-Za-z]:")
        if not drive_letter_pattern.match(self.path_parts[0]):
            raise ValueError(f"Invalid or missing drive letter in the path: '{self.path}'")


class MacOS(BaseService):
    invalid_characters = ''  # No additional invalid characters besides path delimiters

    def __init__(self, path, auto_clean=False):
        super().__init__(path, auto_clean)
        self.restricted_names = {".DS_Store", "._myfile"}  # Common Mac reserved names

    def validate(self):
        """Validate the path for MacOS-specific restrictions."""
        self.validate_empty_parts()
        self.validate_if_whitespace_around_parts()
        self.validate_restricted_names()

    def clean(self, raise_error=True):
        """Clean and return the MacOS-compliant path, and validate if raise_error is True."""
        cleaned_path = super().clean(raise_error=raise_error)
        cleaned_path = self.get_validate_or_clean_method("restricted_names", "clean", path=cleaned_path)

        if raise_error:
            cleaned_path_instance = MacOS(cleaned_path)
            cleaned_path_instance.validate()

        return cleaned_path


class Linux(BaseService):
    invalid_characters = '\0'  # Only null character is invalid on Linux

    def __init__(self, path, auto_clean=False):
        super().__init__(path, auto_clean)
        
        self.corresponding_validate_and_clean_methods.update(
            {"null_character": {"validate": "validate_null_character", "clean": "clean_null_character"}}
        )

    def validate_null_character(self):
        """Check if the path contains a null character."""
        if '\0' in self.path:
            raise ValueError('Null character "\\0" is not allowed in Linux file paths.')
        
    def clean_null_character(self):
        """Remove null characters from the path."""
        return self.path.replace('\0', '')

    def validate(self):
        """Validate the path for Linux-specific restrictions."""
        self.validate_empty_parts()
        self.validate_if_whitespace_around_parts()

       # validate null character
        self.validate_null_character()

    def clean(self, raise_error=True):
        """Clean and return the Linux-compliant path, and validate if raise_error is True."""
        # so fresh and so clean clean (clean) lmao
        # she is super clean, super clean! 
        # sorry... I've been working for 12 hours now. :) brain no doin brain stuffs
        cleaned_path = super().clean(raise_error=raise_error)
        cleaned_path = cleaned_path.replace('\0', '')

        if raise_error:
            cleaned_path_instance = Linux(cleaned_path)
            cleaned_path_instance.validate()

        return cleaned_path
