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

    def __init__(self, path: str, sep: str = '/', auto_clean: bool = False, auto_validate: bool = True, relative: bool = True):
        self._path_helper = Path(initial_path=path, sep=sep, relative=relative)
        self.auto_clean = auto_clean
        self.auto_validate = auto_validate
        self.sep = sep
        self.path = self._path_helper.get_full_path()

        if self.auto_clean:
            self.clean()
        if self.auto_validate:
            self.validate()

    def get_logs(self) -> Dict[str, List[dict]]:
        """Retrieve logs from Path helper."""
        return self._path_helper.get_logs()
    
    def add_part(self, part: str, is_file: bool = False, mode: str = "validate"):
        """Add a new part to the path, process it, and check overall validity."""
        self._path_helper.add_part(part, is_file=is_file)

        # Process the specific part (validate or clean based on mode)
        if mode.lower() == "validate":
            self.validate()  # Revalidate the path after addition
        elif mode.lower() == "clean":
            self.clean()

        # Always check path length after every modification
        self.process_path_length(action="validate" if mode == "validate" else "clean")

    def remove_part(self, index: int, mode: str = "validate"):
        """Remove a part from the path, process remaining, and check validity."""
        self._path_helper.remove_part(index)

        # Validate or clean the remaining path
        if mode.lower() == "validate":
            self.validate()  # Revalidate the path after removal
        elif mode.lower() == "clean":
            self.clean()

        # Always check path length after modification
        self.process_path_length(action="validate" if mode == "validate" else "clean")

    def process_invalid_characters(self, action: str):
        """Process invalid characters based on the specified action."""
        for i, part in enumerate(self._path_helper.parts):
            # Delegate root folder logic to subclasses if path is absolute
            if not self._path_helper.relative and i == 0:
                self.process_root_folder_format(part, action)
                continue

            # Find invalid characters in the current part
            invalid_chars = [char for char in part if char in self.invalid_characters]
            if invalid_chars:
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "type": "issue",
                            "category": "INVALID_CHAR",
                            "details": {"part": part, "invalid_chars": invalid_chars},
                            "reason": f"Invalid characters {invalid_chars} found in part: '{part}'.",
                        }
                    )
                elif action == "clean":
                    cleaned_part = ''.join(char for char in part if char not in self.invalid_characters)
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "INVALID_CHAR",
                            "subtype": "MODIFY",
                            "details": {"original": part, "new_value": cleaned_part},
                            "reason": "Removed invalid characters.",
                        },
                        priority=2  # Priority for invalid character cleanups
                    )

    def process_root_folder_format(self, root: str, action: str):
        """Process the root folder format based on acceptable patterns."""
        if not self.acceptable_root_patterns:
            raise NotImplementedError(
                "Subclasses must define acceptable_root_patterns to validate root formats."
            )

        valid = any(re.match(pattern, root) for pattern in self.acceptable_root_patterns)

        if not valid:
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "ROOT_FORMAT",
                        "details": {"root": root},
                        "reason": f"Root '{root}' does not match any acceptable pattern: {self.acceptable_root_patterns}.",
                    }
                )
            elif action == "clean":
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "ROOT_FORMAT",
                        "subtype": "REMOVE",
                        "priority": 0,
                        "details": {"part": root},
                        "reason": "Removed invalid root folder.",
                    }
                )

    def process_path_length(self, action: str):
        """Process path length based on the specified action."""
        if not self._path_helper.check_path_length(self.max_length):
            return  # Skip if within the limit

        if action == "validate":
            self._path_helper.add_issue(
                {
                    "type": "issue",
                    "category": "PATH_LENGTH",
                    "details": {"current_length": self._path_helper.path_length, "max_length": self.max_length},
                    "reason": f"Path exceeds maximum length of {self.max_length} characters.",
                }
            )
        elif action == "clean":
            cumulative_length = 0

            for i, part in enumerate(self._path_helper.parts):
                part_length = len(part)
                separator_length = 1 if i > 0 else 0

                if cumulative_length + part_length + separator_length > self.max_length:
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "PATH_LENGTH",
                            "subtype": "REMOVE",
                            "details": {"part": part, "index": i},
                            "reason": f"Marked part '{part}' for removal due to exceeding path length limit.",
                        },
                        priority=1
                    )
                else:
                    cumulative_length += part_length + separator_length

    def process_restricted_names(self, action: str):
        """Process restricted names based on the specified action."""
        for i, part in enumerate(self._path_helper.parts):
            # Check if the part is a restricted name
            if part.lower() in [name.lower() for name in self.restricted_names]:
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "type": "issue",
                            "category": "RESTRICTED_NAME",
                            "subtype": "REPORT",
                            "details": {"part": part},
                            "reason": f"Restricted name '{part}' found in path.",
                        }
                    )
                elif action == "clean":
                    self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "RESTRICTED_NAME",
                        "subtype": "REMOVE",
                        "priority": 2,  # Priority for restricted names processing
                        "details": {"part": part, "index": i},
                        "reason": f"Removed restricted name '{part}' to avoid conflicts.",
                    }
                )

    def process_trailing_periods(self, action: str):
        """Process trailing periods in path parts based on the specified action."""
        for i, part in enumerate(self._path_helper.parts):
            if part.endswith('.'):
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "type": "issue",
                            "category": "TRAILING_PERIOD",
                            "subtype": "REPORT",
                            "details": {"part": part, "index": i},
                            "reason": f"The part '{part}' ends with a trailing period, which is not allowed.",
                        }
                    )
                elif action == "clean":
                    cleaned_part = part.rstrip('.')
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "TRAILING_PERIOD",
                            "subtype": "MODIFY",
                            "priority": 3,  # Priority for processing trailing periods
                            "details": {"original": part, "new_value": cleaned_part, "index": i},
                            "reason": f"Removed trailing period from '{part}'.",
                        }
                    )

    def process_whitespace(self, action: str):
        """
        Process leading/trailing whitespace in each part of the path, including around file extensions.
        """
        for i, part in enumerate(self._path_helper.parts):
            is_file = self._path_helper.file_added and i == len(self._path_helper.parts) - 1

            # Remove leading/trailing whitespace
            cleaned_part = part.strip()

            # Handle whitespace around file extensions if part is a file
            if is_file and '.' in cleaned_part:
                name, ext = '.'.join(cleaned_part.split('.')[:-1]).strip(), cleaned_part.split('.')[-1].strip()
                cleaned_part = f"{name}.{ext}"

            # Check if the part was modified
            if part != cleaned_part:
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "category": "WHITESPACE",
                            "subtype": "MODIFY",
                            "details": {"part": part, "index": i},
                            "reason": (
                                f"Whitespace detected in part: '{part}'. "
                                f"Leading/trailing whitespace or whitespace around file extension removed."
                            ),
                        }
                    )
                elif action == "clean":
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "WHITESPACE",
                            "subtype": "MODIFY",
                            "priority": 2,
                            "details": {"original": part, "new_value": cleaned_part},
                            "reason": "Removed whitespace from part of path.",
                        }
                    )

    def process_empty_parts(self, action: str):
        """
        Process empty parts in the path based on the specified action.
        """
        for i, part in enumerate(self._path_helper.parts):
            if part == "":
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "type": "issue",
                            "category": "EMPTY_PART",
                            "subtype": "REMOVE",
                            "details": {"index": i},
                            "reason": f"Empty part found at index {i} in the path.",
                        }
                    )
                elif action == "clean":
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "EMPTY_PART",
                            "subtype": "REMOVE",
                            "priority": 1,
                            "details": {"index": i},
                            "reason": f"Removed empty part at index {i} from the path.",
                        }
                    )
    
    def clean(self):
        """
        Apply all queued actions from the Path helper to clean the path.
        """
        self._path_helper.apply_actions()  # Clean the path by applying queued actions
        return self.get_full_path()

    def validate(self):
        """
        Validate the path by checking for issues and raising a ValueError if any exist.
        """
        issues = self._path_helper.get_logs()["issues"]
        if issues:
            # Raise a ValueError with a JSON dump of the issues
            raise ValueError(
                "Validation failed with the following issues:\n" + json.dumps(issues, indent=4)
            )
        return True  # If no issues, validation passed

    def get_full_path(self) -> str:
        """
        Retrieve the full path after applying all actions.
        """
        return self._path_helper.get_full_path()
