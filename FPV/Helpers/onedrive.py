from FPV.Helpers._base import FPV_Base


class FPV_OneDrive(FPV_Base):
    # OneDrive-specific rules
    invalid_characters = "#%&*:{}<>?|\""
    max_length = 400
    restricted_names = {
        ".lock", "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5",
        "COM6", "COM7", "COM8", "COM9", "LPT1",
        "LPT2", "LPT3", "LPT4", "LPT5", "LPT6",
        "LPT7", "LPT8", "LPT9", "_vti_", "desktop.ini"
    }
    restricted_prefix = "~$"
    acceptable_root_patterns = [r"^root$"]

    def __init__(self, path, **kwargs):
        sep = kwargs.get("sep", "/")  # Default separator is "/"
        # Check if the first part of the path is explicitly "root"
        if path.split(sep)[0] != "root" if path.split(sep) else True:
            kwargs.pop("relative", None)  # Remove relative argument
            super().__init__(path, relative=True, **kwargs)
        else:
            super().__init__(path, **kwargs)

    def processing_methods(self):
        """Define the processing methods for OneDrive paths."""
        return {
            "root": [
            ],
            "folder": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_path_length(part, action),
                lambda part, action: self.process_restricted_prefix(part, action),
            ],
            "file": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_path_length(part, action),
                lambda part, action: self.process_restricted_prefix(part, action),
            ],
        }

    def process_restricted_prefix(self, part: dict, action: str):
        """Process path parts with restricted prefixes."""
        part_str = part["part"]
        index = part["index"]
        if part_str.startswith(self.restricted_prefix):
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "RESTRICTED_PREFIX",
                        "details": {"part": part_str, "index": index},
                        "reason": f'Restricted prefix "{self.restricted_prefix}" found in path part.',
                    }
                )
            elif action == "clean":
                cleaned_part = part_str[len(self.restricted_prefix):]
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "RESTRICTED_PREFIX",
                        "subtype": "MODIFY",
                        "priority": 2,
                        "details": {"original": part_str, "new_value": cleaned_part, "index": index},
                        "reason": f'Removed restricted prefix "{self.restricted_prefix}" from path part.',
                    },
                    priority=2
                )
                return cleaned_part
        return part_str
