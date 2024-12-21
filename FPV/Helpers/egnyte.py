import re
from FPV.Helpers._base import FPV_Base


class FPV_Egnyte(FPV_Base):
    # Egnyte-specific character restrictions
    invalid_characters = ':*?"<>|'
    max_length = 5000  # Max path length
    part_length = 245  # Max length per path part
    acceptable_root_patterns = [r"^[A-Za-z]:\\$", r"^[A-Za-z]:/$"]  # Adjust if necessary for Egnyte

    restricted_names = {
        ".ds_store", ".metadata_never_index", ".thumbs.db",
        "powerpoint temp", "desktop.ini", "icon\r", ".data", ".tmp"
    }
    endings = [
        ".", "~", "._attribs_", "._rights_", "._egn_", "_egnmeta",
        ".tmp", "-spotlight", ".ac$", ".sv$", ".~vsdx"
    ]
    starts = ["._", ".~", "word work file", "_egn_.", ".smbdelete", ".spotlight-"]
    starts_with_tilde_endings = [".idlk", ".xlsx", ".pptx"]
    starts_with_tilde_dollar_endings = [
        ".doc", ".docx", ".rtf", ".ppt", ".pptx",
        ".xlsm", ".sldlfp", ".slddrw", ".sldprt", ".sldasm"
    ]
    temp_patterns = [
        r"^atmp\d{4}$",  # AutoCAD temp files, e.g., "atmp3829"
        r"^.+\.sas\.b\d{2}$",  # SAS temp files, e.g., "myFile.sas.b73"
        r"^aa[a-zA-Z]\d{5}$",  # PDF temp files, e.g., "aau38221"
        r"^.+\.\$\$\$$"  # Files ending in .$$$, e.g., "myFile.$$$"
    ]

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)

    def process_part_length(self, action: str):
        """Process part length based on Egnyte's restrictions."""
        for i, part in enumerate(self._path_helper.parts):
            if len(part) > self.part_length:
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "type": "issue",
                            "category": "PART_LENGTH",
                            "details": {"part": part, "index": i},
                            "reason": f"Part '{part}' exceeds maximum length of {self.part_length} characters.",
                        }
                    )
                elif action == "clean":
                    truncated_part = part[:self.part_length]
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "PART_LENGTH",
                            "subtype": "MODIFY",
                            "priority": 2,
                            "details": {"original": part, "new_value": truncated_part, "index": i},
                            "reason": f"Truncated part '{part}' to meet length requirements.",
                        }
                    )

    def process_restricted_suffixes(self, action: str):
        """Process restricted Egnyte suffixes."""
        for i, part in enumerate(self._path_helper.parts):
            if any(part.lower().endswith(suffix) for suffix in self.endings):
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "type": "issue",
                            "category": "SUFFIX",
                            "details": {"part": part, "index": i},
                            "reason": f"Part '{part}' has a restricted suffix.",
                        }
                    )
                elif action == "clean":
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "SUFFIX",
                            "subtype": "REMOVE",
                            "priority": 3,
                            "details": {"part": part, "index": i},
                            "reason": f"Removed part '{part}' due to restricted suffix.",
                        }
                    )

    def process_restricted_prefixes(self, action: str):
        """Process restricted Egnyte prefixes."""
        for i, part in enumerate(self._path_helper.parts):
            if any(part.lower().startswith(prefix) for prefix in self.starts):
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "type": "issue",
                            "category": "PREFIX",
                            "details": {"part": part, "index": i},
                            "reason": f"Part '{part}' has a restricted prefix.",
                        }
                    )
                elif action == "clean":
                    cleaned_part = part
                    for prefix in self.starts:
                        if cleaned_part.lower().startswith(prefix):
                            cleaned_part = cleaned_part[len(prefix):]
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "PREFIX",
                            "subtype": "MODIFY",
                            "priority": 3,
                            "details": {"original": part, "new_value": cleaned_part, "index": i},
                            "reason": f"Removed restricted prefix from part '{part}'.",
                        }
                    )

    def process_temp_patterns(self, action: str):
        """Process restricted temporary file patterns."""
        for i, part in enumerate(self._path_helper.parts):
            if any(re.match(pattern, part.lower()) for pattern in self.temp_patterns):
                if action == "validate":
                    self._path_helper.add_issue(
                        {
                            "type": "issue",
                            "category": "TEMP_PATTERN",
                            "details": {"part": part, "index": i},
                            "reason": f"Part '{part}' matches a restricted temporary file pattern.",
                        }
                    )
                elif action == "clean":
                    self._path_helper.add_action(
                        {
                            "type": "action",
                            "category": "TEMP_PATTERN",
                            "subtype": "REMOVE",
                            "priority": 4,
                            "details": {"part": part, "index": i},
                            "reason": f"Removed part '{part}' due to restricted temporary file pattern.",
                        }
                    )

    def validate(self):
        """Validate the path according to Egnyte-specific rules."""
        self.process_path_length(action="validate")
        self.process_invalid_characters(action="validate")
        self.process_restricted_names(action="validate")
        self.process_restricted_suffixes(action="validate")
        self.process_restricted_prefixes(action="validate")
        self.process_temp_patterns(action="validate")
        self.process_part_length(action="validate")
        self.process_whitespace(action="validate")
        self.process_empty_parts(action="validate")
        super().validate()

    def clean(self, raise_error=True):
        """Clean and return an Egnyte-compliant path; validate if `raise_error` is True."""
        self.process_path_length(action="clean")
        self.process_invalid_characters(action="clean")
        self.process_restricted_names(action="clean")
        self.process_restricted_suffixes(action="clean")
        self.process_restricted_prefixes(action="clean")
        self.process_temp_patterns(action="clean")
        self.process_part_length(action="clean")
        self.process_whitespace(action="clean")
        self.process_empty_parts(action="clean")
        if raise_error:
            self.validate()
        return super().clean()
