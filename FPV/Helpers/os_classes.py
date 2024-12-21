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
    acceptable_root_patterns = [r"^[A-Za-z]:$", r"^[A-Za-z]:\\$"]

    def __init__(self, path, **kwargs):
        super().__init__(path, sep="\\", **kwargs)

    def processing_methods(self):
        """Define the processing methods for Windows paths."""
        return [
            lambda part, action: self.process_root_folder_format(part, action),
            lambda part, action: self.process_invalid_characters(part, action),
            lambda part, action: self.process_restricted_names(part, action),
            lambda part, action: self.process_whitespace(part, action),
            lambda part, action: self.process_empty_parts(part, action),
            lambda part, action: self.process_trailing_periods(part, action),
            lambda part, action: self.process_path_length(part, action),
        ]


class FPV_MacOS(FPV_Base):
    # MacOS-specific invalid characters (no additional invalid characters apart from path delimiters)
    invalid_characters = ""

    # Reserved file/folder names
    restricted_names = {".DS_Store", "._myfile"}

    # Regex for leading periods in folder names
    unacceptable_leading_patterns = [r"^\.+[^/.]+$"]  # e.g., ".hidden_folder" is invalid

    acceptable_root_patterns = [r"^/[^/\0]+$"]

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)

    def process_leading_periods(self, action: str):
        """
        Process leading periods in folder names based on the specified action.
        """
        for i, part in enumerate(self._path_helper.parts):
            # Skip the file check (last part) if this is a file
            if self._path_helper.file_added and i == len(self._path_helper.parts) - 1:
                continue

            # Check if the folder starts with a leading period
            if any(re.match(pattern, part) for pattern in self.unacceptable_leading_patterns):
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "type": "issue",
                            "category": "LEADING_PERIOD",
                            "details": {"part": part, "index": i},
                            "reason": f"Folder name '{part}' starts with a leading period, which is not allowed.",
                        }
                    )
                elif action == "clean":
                    cleaned_part = part.lstrip(".")  # Remove leading periods
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "LEADING_PERIOD",
                            "subtype": "MODIFY",
                            "priority": 2,  # Set appropriate priority
                            "details": {"original": part, "new_value": cleaned_part, "index": i},
                            "reason": f"Removed leading periods from '{part}'.",
                        }
                    )

    def validate(self):
        """Validate the path for MacOS-specific restrictions."""
        self.process_empty_parts(action="validate")
        self.process_whitespace(action="validate")
        self.process_restricted_names(action="validate")
        self.process_leading_periods(action="validate")
        return super().validate()

    def clean(self, raise_error=True):
        """Clean and return the MacOS-compliant path, and validate if raise_error is True."""
        self.process_empty_parts(action="clean")
        self.process_whitespace(action="clean")
        self.process_restricted_names(action="clean")
        self.process_leading_periods(action="clean")

        if raise_error:
            self.validate()

        return super().clean()


class FPV_Linux(FPV_Base):
    # Only null character is invalid in Linux paths
    invalid_characters = '\0'

    acceptable_root_patterns = [r"^/[^/\0]+$"]

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)

    def validate(self):
        """Validate the path for Linux-specific restrictions."""
        self.process_invalid_characters(action="validate")
        self.process_empty_parts(action="validate")
        self.process_whitespace(action="validate")
        return super().validate()

    def clean(self, raise_error=True):
        """Clean and return a Linux-compliant path, and validate if raise_error is True."""
        self.process_invalid_characters(action="clean")
        self.process_empty_parts(action="clean")
        self.process_whitespace(action="clean")

        if raise_error:
            self.validate()

        return super().clean()
