from FPV.Helpers._base import FPV_Base


class FPV_SharePoint(FPV_Base):
    # Invalid characters specific to SharePoint, adding "#" to the base invalid characters
    invalid_characters = FPV_Base.invalid_characters + "#"
    max_length = 400
    acceptable_root_patterns = [r"^forms$", r"^/$"]  # Allow "forms" as root folder or root "/"
    restricted_names = {
        ".lock", "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5",
        "COM6", "COM7", "COM8", "COM9", "LPT1",
        "LPT2", "LPT3", "LPT4", "LPT5", "LPT6",
        "LPT7", "LPT8", "LPT9", "_vti_", "desktop.ini"
    }
    restricted_prefix = "~$"
    restricted_root_folder = "forms"

    def __init__(self, path: str, **kwargs):
        super().__init__(path, **kwargs)

    def validate(self):
        """Validate the full path for SharePoint, including SharePoint-specific validations."""
        self.process_path_length(action="validate")
        self.process_invalid_characters(action="validate")
        self.process_restricted_names(action="validate")
        self.process_whitespace(action="validate")
        self.process_trailing_periods(action="validate")
        self.process_empty_parts(action="validate")
        self.process_restricted_prefix(action="validate")
        self.process_restricted_root(action="validate")
        super().validate()

    def clean(self, raise_error=True):
        """Clean the path to be SharePoint-compliant and validate if `raise_error` is True."""
        self.process_path_length(action="clean")
        self.process_invalid_characters(action="clean")
        self.process_restricted_names(action="clean")
        self.process_whitespace(action="clean")
        self.process_trailing_periods(action="clean")
        self.process_empty_parts(action="clean")
        self.process_restricted_prefix(action="clean")
        self.process_restricted_root(action="clean")
        if raise_error:
            self.validate()
        return super().clean()

    def process_restricted_prefix(self, action: str):
        """Process parts with restricted prefixes for SharePoint."""
        for i, part in enumerate(self._path_helper.parts):
            if part.startswith(self.restricted_prefix):
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "type": "issue",
                            "category": "RESTRICTED_PREFIX",
                            "details": {"part": part, "index": i},
                            "reason": f"Part '{part}' starts with restricted prefix '{self.restricted_prefix}'.",
                        }
                    )
                elif action == "clean":
                    cleaned_part = part[len(self.restricted_prefix):]
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "RESTRICTED_PREFIX",
                            "subtype": "MODIFY",
                            "priority": 2,
                            "details": {"original": part, "new_value": cleaned_part, "index": i},
                            "reason": f"Removed restricted prefix '{self.restricted_prefix}' from part.",
                        }
                    )

    def process_restricted_root(self, action: str):
        """Process restricted root folders for SharePoint."""
        if self._path_helper.parts and self._path_helper.parts[0].lower() == self.restricted_root_folder:
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "RESTRICTED_ROOT",
                        "details": {"part": self._path_helper.parts[0], "index": 0},
                        "reason": f"Restricted root folder '{self.restricted_root_folder}' is not allowed as the first part.",
                    }
                )
            elif action == "clean":
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "RESTRICTED_ROOT",
                        "subtype": "REMOVE",
                        "priority": 1,
                        "details": {"part": self._path_helper.parts[0], "index": 0},
                        "reason": f"Removed restricted root folder '{self.restricted_root_folder}' from the path.",
                    }
                )
