import re
import json
from typing import List, Dict
from ._path import Path

class FPV_Base:
    """Base class for path validation and cleaning."""

    # Default configurations
    invalid_characters = ""
    max_length = 0
    restricted_names: set = set()
    acceptable_root_patterns: List[str] = []

    def __init__(self, path: str, sep: str = '/', auto_validate: bool = True, auto_clean: bool = False, relative: bool = True, file_added: bool = False):
        self._path_helper = Path(initial_path=path.strip(sep), sep=sep, relative=relative, file_added=file_added)
        self.auto_validate = auto_validate
        self.auto_clean = auto_clean
        self.sep = sep
        self.file_added = file_added
        self.path = self._path_helper.get_full_path()

        # clean before validating
        if self.auto_clean:
            self.clean()

        # this is an elif because clean already validates the path upon cleaning
        elif self.auto_validate:
            self.validate()

    def get_logs(self) -> Dict[str, List[dict]]:
        """Retrieve logs from Path helper."""
        return self._path_helper.get_logs()
    
    def add_part(self, part: str, is_file: bool = False, mode: str = "validate"):
        """Add a new part to the path, process it, and check overall validity."""
        self._path_helper.add_part(part, is_file=is_file)

        # Process the specific part (validate or clean based on mode)
        if mode.lower() == "clean" or self.auto_clean:
            self.clean()  # Clean the path after addition
        if mode.lower() == "validate" or self.auto_validate:
            self.validate()  # Revalidate the path after addition

        # Always check path length after every modification
        self.process_path_length(self._path_helper.parts[-1], action="validate" if mode == "validate" else "clean")

    def remove_part(self, index: int, mode: str = "validate"):
        """Remove a part from the path, process remaining, and check validity."""
        self._path_helper.remove_part(index)
        
        # Process the specific part (validate or clean based on mode)
        if mode.lower() == "clean" or self.auto_clean:
            self.clean()  # Clean the path after addition
        if mode.lower() == "validate" or self.auto_validate:
            self.validate()  # Revalidate the path after addition
        
        self.process_path_length(part={}, action="validate" if mode == "validate" else "clean")

    def process_invalid_characters(self, part: dict, action: str):
        """Process invalid characters for a specific part based on the specified action."""
        part_str = part["part"]
        index = part["index"]
        invalid_chars = [char for char in part_str if char in self.invalid_characters]

        if invalid_chars:
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "INVALID_CHAR",
                        "details": {"part": part_str, "invalid_chars": invalid_chars, "index": index},
                        "reason": f"Invalid characters {invalid_chars} found in part: '{part_str}'.",
                    }
                )
            elif action == "clean":
                cleaned_part = ''.join(char for char in part_str if char not in self.invalid_characters)
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "INVALID_CHAR",
                        "subtype": "MODIFY",
                        "details": {"original": part_str, "new_value": cleaned_part, "index": index},
                        "reason": "Removed invalid characters.",
                    },
                    priority=2
                )
                return cleaned_part  # Return the cleaned part to replace the original
        return part_str

    def process_root_folder_format(self, part: dict, action: str):
        """Process the root folder format based on acceptable patterns."""
        part_str = part["part"]
        index = part["index"]
        if self._path_helper.relative or index != 0:
            return part_str

        valid = any(re.match(pattern, part_str) for pattern in self.acceptable_root_patterns) if self.acceptable_root_patterns else True

        if not valid:
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "ROOT_FORMAT",
                        "details": {"root": part_str},
                        "reason": f"Root '{part_str}' does not match any acceptable pattern: {self.acceptable_root_patterns}.",
                    }
                )
            elif action == "clean":
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "ROOT_FORMAT",
                        "subtype": "REMOVE",
                        "details": {"part": part_str},
                        "reason": "Removed invalid root folder.",
                    },
                    priority=0
                )
                return ''  # Return empty string to remove the part
        return part_str

    def process_path_length(self, part: dict, action: str):
        """Process part or overall path length based on the specified action."""
        part_str = part.get("part", "")
        if not part: 
            # check to see if current path length is within the max length
            # if it is and no part was passed, then we are probably in removal mode. 
            # if so, we should check the path length after the part is removed.
            # if we are good now, then we can remove all issues related to path length.
            if self._path_helper.path_length <= self.max_length:
                self._path_helper.remove_all_issues(issue_type="PATH_LENGTH")
            return part_str

        index = part["index"]
        # calculate path length instead for full precision
        current_length = 0
        for index_of_iteration, part in enumerate(self._path_helper.parts):
            if index_of_iteration == index:
                break
            current_length += len(part["part"]) + len(self.sep)
        part_length = len(part_str)

        if action == "validate" and current_length + part_length + len(self.sep) > self.max_length:
            self._path_helper.add_issue(
                {
                    "type": "issue",
                    "category": "PATH_LENGTH",
                    "details": {"current_length": current_length, "max_length": self.max_length, "index": index, "part": part_str},
                    "reason": f"Path exceeds maximum length of {self.max_length} characters.",
                }
            )
        elif action == "clean":
            remaining_length = self.max_length - (current_length + len(part_str))
            if remaining_length <= 0 or (remaining_length < len(part_str) and index == (len(self._path_helper.parts) - 1)):
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "PATH_LENGTH",
                        "subtype": "REMOVE",
                        "details": {"current_length": current_length, "max_length": self.max_length, "index": index, "part": part_str},
                        "reason": f"Removed '{part_str}' to reduce path length to within {self.max_length} characters.",
                    },
                    priority=1
                )
                return ''  # Return empty string to remove the part
            else:
                truncated_part = part_str[:remaining_length]
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "PATH_LENGTH",
                        "subtype": "MODIFY",
                        "details": {"original": part_str, "new_value": truncated_part, "index": index},
                        "reason": f"Truncated '{part_str}' to '{truncated_part}' to reduce path length.",
                    },
                    priority=1
                )
                return truncated_part  # Return the truncated part to replace the original
        return part_str

    def process_restricted_names(self, part: dict, action: str):
        """Process restricted names for a specific part based on the specified action."""
        part_str = part["part"]
        index = part["index"]
        if part_str.lower() in [name.lower() for name in self.restricted_names]:
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "RESTRICTED_NAME",
                        "details": {"part": part_str, "index": index},
                        "reason": f"Restricted name '{part_str}' found in path.",
                    }
                )
            elif action == "clean":
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "RESTRICTED_NAME",
                        "subtype": "REMOVE",
                        "details": {"index": index, "part": part_str},
                        "reason": f"Removed restricted name '{part_str}' to avoid conflicts.",
                    },
                    priority=2
                )
                return ''  # Return empty string to remove the part
        return part_str

    def process_trailing_periods(self, part: dict, action: str):
        """Process trailing periods for a specific part based on the specified action."""
        part_str = part["part"]
        index = part["index"]
        if part_str.endswith('.'):
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "TRAILING_PERIOD",
                        "details": {"part": part_str, "index": index},
                        "reason": f"The part '{part_str}' ends with a trailing period.",
                    }
                )
            elif action == "clean":
                cleaned_part = part_str.rstrip('.')
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "TRAILING_PERIOD",
                        "subtype": "MODIFY",
                        "details": {"original": part_str, "new_value": cleaned_part, "index": index},
                        "reason": "Removed trailing period.",
                    },
                    priority=3
                )
                return cleaned_part  # Return the cleaned part to replace the original
        return part_str

    def process_whitespace(self, part: dict, action: str):
        """Process leading/trailing whitespace in a specific part, including file extensions."""
        part_str = part["part"]
        index = part["index"]
        is_file = part.get("is_file", False)
        cleaned_part = part_str.strip()

        if is_file and '.' in cleaned_part:
            name, ext = '.'.join(cleaned_part.split('.')[:-1]).strip(), cleaned_part.split('.')[-1].strip()
            cleaned_part = f"{name}.{ext}"

        if part_str != cleaned_part:
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "WHITESPACE",
                        "details": {"part": part_str, "index": index},
                        "reason": "Whitespace detected in path part.",
                    }
                )
            elif action == "clean":
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "WHITESPACE",
                        "subtype": "MODIFY",
                        "details": {"original": part_str, "new_value": cleaned_part, "index": index},
                        "reason": "Removed whitespace.",
                    },
                    priority=2
                )
                return cleaned_part  # Return the cleaned part to replace the original
        return part_str

    def process_empty_parts(self, part: dict, action: str):
        """Process empty parts in the path."""
        part_str = part["part"]
        index = part["index"]
        part_is_file = part.get("is_file", False)
        if part_str == "":
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "EMPTY_PART",
                        "details": {"index": index},
                        "reason": "Empty part found in the path.",
                    }
                )
            elif action == "clean":
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "EMPTY_PART",
                        "subtype": "REMOVE",
                        "details": {"index": index},
                        "reason": "Removed empty part.",
                    },
                    priority=1
                )
                return ''  # Return empty string to remove the part
        return part_str
    
    def clean(self, validate_after_clean=True, **kwargs):
        """
        Clean the path by processing all unseen or pending parts.

        Args:
            validate_after_clean (bool): If True, validate the path after cleaning.
        
        Returns:
            str: The cleaned path.
        """
        parts_to_clean = self._path_helper.get_parts_to_clean()

        # Override the issues log with a clean slate for the parts we're about to clean.
        self._path_helper.logs["issues"] = self._path_helper.get_issues(clean_mode=True)

        for part in parts_to_clean:
            part_index = part["index"]
            part_type = self._path_helper.get_part_type(part)

            # Get the appropriate processing methods based on the part type
            processing_methods = self.processing_methods().get(part_type, [])

            # Process the part with each method
            for process_method in processing_methods:
                cleaned_item = process_method(part, action="clean")
                self._path_helper.parts[part_index]["part"] = cleaned_item

            # Determine the cleaned status based on pending actions
            pending_actions = self._path_helper.get_pending_actions_for_part(part_index)
            status = "pending" if pending_actions else "complete"
            self._path_helper.mark_part(part_index, state="cleaned_status", status=status)
            self._path_helper.mark_part(part_index, state="checked_status", status="unseen") if validate_after_clean else None
            # mark it as unseen so that validate checks it again if validate_after_clean is True

        cleaned_path = self._path_helper.get_full_path()

        if validate_after_clean:
            self.validate(**kwargs)

        return cleaned_path

    def validate(self, raise_error=True, **kwargs):
        """
        Validate the path by processing all unseen parts.

        Args:
            raise_error (bool): If True, raise an error if validation issues are found.
        
        Returns:
            List[dict]: Validation issues or an empty list if none exist.
        """
        unseen_parts = self._path_helper.get_parts_to_check()

        for part in unseen_parts:
            part_index = part["index"]
            part_type = self._path_helper.get_part_type(part)

            # Get the appropriate processing methods based on the part type
            processing_methods = self.processing_methods().get(part_type, [])

            # Process the part with each method
            for process_method in processing_methods:
                process_method(part, action="validate")

            # Determine the checked status based on validation issues
            issues_for_part = self._path_helper.get_issues_for_part(part_index)
            status = "invalid" if issues_for_part else "complete"
            self._path_helper.mark_part(part_index, state="checked_status", status=status)

        issues = self._path_helper.get_logs().get("issues", [])
        if issues and raise_error:
            raise ValueError(json.dumps(issues, indent=4))

        return issues
    
    def processing_methods(self) -> dict:
        """
        Define the list of processing methods to apply for both cleaning and validation.
        Subclasses must override this method.

        Returns:
            List[Callable]: A list of processing methods.
        """
        raise NotImplementedError("Subclasses must define `processing_methods`.")

    def get_full_path(self) -> str:
        """
        Retrieve the full path after applying all actions.
        """
        return self._path_helper.get_full_path()
