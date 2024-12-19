import re
from typing import List, Dict, Optional
from ._path import Path

class FPV_Base:
    """Base class for path validation and cleaning."""

    # Default configurations
    invalid_characters = ""
    max_length = 0
    restricted_names: set = set()

    def __init__(self, path: str, sep: str = '/', auto_clean: bool = False, auto_validate: bool = True):
        self.path_helper = Path(initial_path=path, sep=sep)
        self.logs: Dict[str, List[dict]] = {"actions": [], "issues": []}

        if auto_clean:
            self.clean()
        if auto_validate:
            self.validate()

    def add_action_or_issue(self, kind: str, subtype: str, details: dict, reason: Optional[str] = None):
        """Log an action or issue."""
        log_entry = {
            "kind": kind,  # "action" or "issue"
            "subtype": subtype,
            "details": details,
            "reason": reason or "No reason provided.",
        }
        self.logs[kind + "s"].append(log_entry)

    def process_invalid_characters(self, action: str):
        """Process invalid characters based on the specified action."""
        for i, part in enumerate(self.path_helper.parts):
            invalid_chars = [char for char in part if char in self.invalid_characters]
            if invalid_chars:
                if action == "validate":
                    self.add_action_or_issue(
                        kind="issue",
                        subtype="INVALID_CHAR",
                        details={"part": part, "invalid_chars": invalid_chars},
                        reason=f"Invalid characters {invalid_chars} found in part: '{part}'.",
                    )
                elif action == "clean":
                    cleaned_part = ''.join(char for char in part if char not in self.invalid_characters)
                    self.add_action_or_issue(
                        kind="action",
                        subtype="INVALID_CHAR",
                        details={"original": part, "new_value": cleaned_part},
                        reason="Removed invalid characters.",
                    )
                    self.path_helper.set_part(i, cleaned_part)


    def remove_invalid_characters(self, path=''):
        """Remove invalid characters from each part of the path and return the cleaned path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        cleaned_parts = []
        for index, part in enumerate(input_path_parts):

            # this is some ugly hard coded bullshit if I'm being honest lol
            if not self.relative and "windows" in self.__class__.__name__.lower():
                if index == 0:
                    self.invalid_characters = self.invalid_characters.replace(":", "")
                else:
                    self.invalid_characters = self.invalid_characters + ':' if ':' not in self.invalid_characters else self.invalid_characters
            
            cleaned_part = re.sub(f"[{re.escape(self.invalid_characters)}]", "", part)
            if cleaned_part:  # Only add non-empty parts
                cleaned_parts.append(cleaned_part)
        output_path = self.sep.join(cleaned_parts)
        return output_path

    def validate_path_length(self, path=''):
        """validate if the path length exceeds the maximum allowed."""
        input_path = self.path if not path else path
        if self.max_length and len(input_path) > self.max_length:
            raise ValueError(f"The specified path is too long. Maximum allowed is {self.max_length} characters.")

    def truncate_path(self, path='', check_files=True):
        """Truncate the path length to meet the maximum length requirement."""
        input_path = self.path if not path else path
        if len(input_path) <= self.max_length:
            return input_path
        
        # Use as much of the filename as possible but raise if the filename alone exceeds max length
        if check_files:
            filename = input_path.split(self.sep)[-1]
            filename_length = len(filename)
            if filename_length > self.max_length:
                raise ValueError(f"The filename is too long. Maximum allowed is {self.max_length} characters.")

            # Calculate maximum usable path length minus filename
            max_path_length = self.max_length - filename_length - 1
            truncated_path = path[:max_path_length]
            
            return f"{self.sep}{truncated_path.strip(self.sep)}{self.sep}{filename.strip(self.sep)}"
        else:
            # just truncate it to the max length after stripping for / signs
            return f"{self.sep}{input_path.strip(self.sep)[:self.max_length]}"

    def validate_restricted_names(self, path=''):
        """validate for restricted names in each part of the path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        for part in input_path_parts:
            if part.lower() in [s.lower() for s in self.restricted_names]:
                raise ValueError(f'Restricted name "{part}" found in path.')

    def remove_restricted_names(self, path=''):
        """Remove restricted names from each part of the path and return the cleaned path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        cleaned_parts = [part for part in input_path_parts if part not in self.restricted_names]
        ouput_path = self.sep.join(cleaned_parts)
        return ouput_path

    def validate_if_part_ends_with_period(self, path=''):
        """validate if any part of the path ends with a period."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        for part in input_path_parts:
            if part.endswith('.'):
                raise ValueError(f'"{part}" cannot end with a period.')

    def remove_trailing_periods(self, path=''):
        """Remove trailing periods from each part of the path and return the cleaned path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        cleaned_parts = [part.rstrip('.') for part in input_path_parts if part.rstrip('.')]
        return self.sep.join(cleaned_parts)

    def validate_if_whitespace_around_parts(self, path=''):
        """validate if there are leading or trailing spaces in any part of the path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        for index, part in enumerate(input_path_parts):
            if part != part.strip():
                raise ValueError(f'Leading or trailing spaces are not allowed in: "{part}".')
            check_files_true = index == len(input_path_parts) - 1 and self.check_files
            if '.' in part and check_files_true:
                before = '.'.join(part.split(".")[:-1])
                after = part.split(".")[-1]
                if before != before.strip() or after != after.strip():
                    raise ValueError(f'Leading or trailing spaces are not allowed around the file extension in: "{part}".')
    
    def remove_whitespace_around_parts(self, path=''):
        """Remove leading and trailing spaces from each part of the path and return the cleaned path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        cleaned_parts = []
        for index, part in enumerate(input_path_parts):
            part = part.strip()
            if '.' in part and self.check_files and index == len(input_path_parts) - 1:
                before = '.'.join(part.split(".")[:-1])
                after = part.split(".")[-1]
                part = f"{before.strip()}.{after.strip()}"
            cleaned_parts.append(part)
        return self.sep.join(cleaned_parts)
                    
    def remove_whitespace_around_part(self, part='', is_file=False):
        """Remove leading and trailing spaces from each part of the path and return the cleaned path."""
        if '.' in part and is_file:
            before = '.'.join(part.split(".")[:-1])
            after = part.split(".")[-1]
            part = f"{before.strip()}.{after.strip()}"
        return part.strip()

    def validate_empty_parts(self, path=''):
        """validate for empty parts in the path."""
        input_path = self.path if not path else path
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        if '' in input_path_parts:
            raise ValueError('Empty parts are not allowed in the path.')

    def remove_empty_parts(self, path=''):
        """Remove any empty parts in the path and return the cleaned path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        cleaned_parts = [part for part in input_path_parts if part]
        output_path = self.sep.join(cleaned_parts)
        return output_path

    def validate(self, path=''):
        return True

    def clean(self, raise_error=True, path=''):
        return self.path
