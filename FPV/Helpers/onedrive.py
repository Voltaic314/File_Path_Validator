from FPV.Helpers._base import FPV_Base


class FPV_OneDrive(FPV_Base):
    # OneDrive-specific rules
    invalid_characters = FPV_Base.invalid_characters + "#%&*:{}<>?|\""
    max_length = 400
    restricted_names = {
        ".lock", "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5",
        "COM6", "COM7", "COM8", "COM9", "LPT1",
        "LPT2", "LPT3", "LPT4", "LPT5", "LPT6",
        "LPT7", "LPT8", "LPT9", "_vti_", "desktop.ini"
    }
    restricted_prefix = "~$"
    restricted_root_level_folder = "forms"
    acceptable_root_patterns = [r"^/$", r"^/root$"]

    def __init__(self, path: str, **kwargs):
        super().__init__(path, **kwargs)

    def validate(self):
        """Validate the path for OneDrive-specific rules."""
        self.process_path_length(action="validate")
        self.process_invalid_characters(action="validate")
        self.process_restricted_names(action="validate")
        self.process_whitespace(action="validate")
        self.process_empty_parts(action="validate")
        self.process_restricted_prefix(action="validate")
        self.process_restricted_root(action="validate")

        return super().validate()

    def clean(self, raise_error=True):
        """Clean and return a OneDrive-compliant path."""
        self.process_path_length(action="clean")
        self.process_invalid_characters(action="clean")
        self.process_restricted_names(action="clean")
        self.process_whitespace(action="clean")
        self.process_empty_parts(action="clean")
        self.process_restricted_prefix(action="clean")
        self.process_restricted_root(action="clean")

        if raise_error:
            self.validate()

        return super().clean()

    def process_restricted_prefix(self, action: str):
        """Process path parts with restricted prefixes."""
        for i, part in enumerate(self._path_helper.parts):
            if part.startswith(self.restricted_prefix):
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "category": "RESTRICTED_PREFIX",
                            "subtype": "REPORT",
                            "details": {"part": part, "index": i},
                            "reason": f'Restricted prefix "{self.restricted_prefix}" found in path part.',
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
                            "reason": f'Removed restricted prefix "{self.restricted_prefix}" from path part.',
                        }
                    )

    def process_restricted_root(self, action: str):
        """Process restricted root folder names."""
        if self._path_helper.parts and self._path_helper.parts[0].lower() == self.restricted_root_level_folder:
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "category": "RESTRICTED_ROOT",
                        "subtype": "REPORT",
                        "details": {"part": self._path_helper.parts[0], "index": 0},
                        "reason": f'Restricted root folder "{self.restricted_root_level_folder}" found at path root.',
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
                        "reason": f'Removed restricted root folder "{self.restricted_root_level_folder}" from path.',
                    }
                )
