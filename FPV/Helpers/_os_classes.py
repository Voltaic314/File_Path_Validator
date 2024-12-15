import re
from FPV.Helpers._base import FPV_Base


class FPV_Windows(FPV_Base):
    invalid_characters = '<>:"|?*'
    max_length = 255
    restricted_names = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", 
        "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", 
        "LPT6", "LPT7", "LPT8", "LPT9"
    }

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)
        self.init_kwargs = kwargs
        self.sep = kwargs.get("sep", "\\")
        if not self.relative:
            if self.path.startswith(self.sep):
                self.path = self.path[1:] # this should fix any weird "/C:/" paths due to the base formatting it does :) 

        if self.auto_clean:
            self.path = self.clean()

    def validate(self, path='', relative=None):
        """Validate the full path for Windows, including Windows-specific validations."""
        input_path = path if path else self.path
        check_drive_letter = not self.relative if relative is None else not relative
        if check_drive_letter:
            self.validate_drive_letter(path=input_path)
        
        self.validate_path_length(path=input_path)
        self.validate_invalid_characters(path=input_path)
        self.validate_restricted_names(path=input_path)
        
        # Validate each part does not end with a period and has no leading/trailing spaces
        self.validate_if_part_ends_with_period(path=input_path)
        self.validate_if_whitespace_around_parts(path=input_path)

        self.validate_empty_parts(path=input_path)

    def clean(self, path='', raise_error=True):
        """Clean and return the Windows-compliant path, and validate if raise_error is True."""
        cleaned_path = path if path else self.path
        cleaned_path = self.clean_and_validate_path("path_length", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("invalid_characters", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("restricted_names", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("whitespace_around_parts", path=cleaned_path)
        
        
        # Remove trailing periods and spaces
        cleaned_path_parts = []
        path_parts = cleaned_path.split(self.sep)
        for part in path_parts:
            cleaned_part = self.remove_trailing_periods(part)
            if cleaned_part:
                cleaned_path_parts.append(cleaned_part)
        cleaned_path = self.sep.join(cleaned_path_parts)

        cleaned_path = self.remove_empty_parts(cleaned_path)
        cleaned_path = f"{self.sep}{cleaned_path}" if self.relative else cleaned_path

        # Validate cleaned path if needed
        if raise_error:
            # pop auto clean from kwargs 
            self.init_kwargs.pop("auto_clean", None)
            cleaned_path_instance = FPV_Windows(cleaned_path, **self.init_kwargs)
            cleaned_path_instance.validate()

        return cleaned_path

    def validate_drive_letter(self, path=''):
        """Verify that the path starts with a valid drive letter (Windows-specific)."""
        input_path = path if path else self.path
        input_path_parts = input_path.strip(self.sep).split(self.sep)
        drive_letter_pattern = re.compile(r"^[A-Za-z]:")
        if not drive_letter_pattern.match(input_path_parts[0]):
            raise ValueError(f"Invalid or missing drive letter in the path: '{self.path}'")


class FPV_MacOS(FPV_Base):
    invalid_characters = ''  # No additional invalid characters besides path delimiters

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)
        self.restricted_names = {".DS_Store", "._myfile"}  # Common Mac reserved names
        self.init_kwargs = kwargs

        if self.auto_clean:
            self.path = self.clean()

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
            # pop auto clean from kwargs 
            self.init_kwargs.pop("auto_clean", None)
            cleaned_path_instance = FPV_MacOS(cleaned_path, **self.init_kwargs)
            cleaned_path_instance.validate()

        return cleaned_path


class FPV_Linux(FPV_Base):
    invalid_characters = '\0'  # Only null character is invalid on Linux

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)
        self.init_kwargs = kwargs
        
        self.corresponding_validate_and_clean_methods.update(
            {"null_character": {"validate": "validate_null_character", "clean": "clean_null_character"}}
        )

        if self.auto_clean:
            self.path = self.clean()

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
            # pop auto clean from kwargs 
            self.init_kwargs.pop("auto_clean", None)
            cleaned_path_instance = FPV_Linux(cleaned_path, **self.init_kwargs)
            cleaned_path_instance.validate()

        return cleaned_path
