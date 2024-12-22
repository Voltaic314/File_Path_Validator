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
        return {
            "root": [
                lambda part, action: self.process_root_folder_format(part, action)
            ],
            "folder": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_trailing_periods(part, action),
                lambda part, action: self.process_path_length(part, action),
            ],
            "file": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_trailing_periods(part, action),
                lambda part, action: self.process_path_length(part, action),
            ],
        }


class FPV_MacOS(FPV_Base):
    # MacOS-specific invalid characters (no additional invalid characters apart from path delimiters)
    invalid_characters = ""

    # Reserved file/folder names
    restricted_names = {".DS_Store", "._myfile"}

    # Regex for leading periods in folder names
    unacceptable_leading_patterns = [r"^\.+[^/.]+$"]  # e.g., ".hidden_folder" is invalid

    # Acceptable root patterns
    acceptable_root_patterns = []

    def __init__(self, path, **kwargs):
        kwargs.pop("relative", None)  # Remove relative argument
        super().__init__(path, relative=True, **kwargs)

    def process_leading_periods(self, part: dict, action: str):
        """Process leading periods in folder names based on the specified action."""
        part_str = part["part"]
        index = part["index"]

        # Skip the file check (last part) if this is a file
        if part.get("is_file", False):
            return part_str

        # Check if the folder starts with a leading period
        if any(re.match(pattern, part_str) for pattern in self.unacceptable_leading_patterns):
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "LEADING_PERIOD",
                        "details": {"part": part_str, "index": index},
                        "reason": f"Folder name '{part_str}' starts with a leading period, which is not allowed.",
                    }
                )
            elif action == "clean":
                cleaned_part = part_str.lstrip(".")  # Remove leading periods
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "LEADING_PERIOD",
                        "subtype": "MODIFY",
                        "priority": 2,  # Set appropriate priority
                        "details": {"original": part_str, "new_value": cleaned_part, "index": index},
                        "reason": f"Removed leading periods from '{part_str}'.",
                    }, 
                    priority=2
                )
                return cleaned_part

        return part_str

    def processing_methods(self):
        """Define the processing methods for MacOS paths."""
        return {
            "root": [
                lambda part, action: self.process_root_folder_format(part, action),
            ],
            "folder": [
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_leading_periods(part, action),
            ],
            "file": [
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_restricted_names(part, action),
            ],
        }


class FPV_Linux(FPV_Base):
    # Only null character is invalid in Linux paths
    invalid_characters = '\0'

    # Acceptable root patterns
    acceptable_root_patterns = []

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)

    def processing_methods(self):
        """Define the processing methods for Linux paths."""
        return {
            "root": [
                lambda part, action: self.process_root_folder_format(part, action),
            ],
            "folder": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_whitespace(part, action),
            ],
            "file": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_whitespace(part, action),
            ],
        }
