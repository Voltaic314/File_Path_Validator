import re
from FPV.Helpers._base import FPV_Base


class FPV_Egnyte(FPV_Base):
    # Egnyte-specific character restrictions
    invalid_characters = ':*?"<>|'
    max_length = 5000  # Max path length
    part_length = 245  # Max length per path part
    acceptable_root_patterns = [r"^[A-Za-z]:$", r"^[A-Za-z]:$"]  # Adjust if necessary for Egnyte

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

    def processing_methods(self):
        """Define the processing methods for Egnyte paths."""
        return {
            "root": [],
            "folder": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_restricted_suffixes(part, action),
                lambda part, action: self.process_restricted_prefixes(part, action),
                lambda part, action: self.process_temp_patterns(part, action),
                lambda part, action: self.process_part_length(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_path_length(part, action),
            ],
            "file": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_restricted_suffixes(part, action),
                lambda part, action: self.process_restricted_prefixes(part, action),
                lambda part, action: self.process_temp_patterns(part, action),
                lambda part, action: self.process_part_length(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_path_length(part, action),
            ],
        }

    def process_restricted_suffixes(self, part: dict, action: str):
        """Process restricted Egnyte suffixes."""
        if any(part["part"].lower().endswith(suffix) for suffix in self.endings):
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "SUFFIX",
                        "details": {"part": part["part"], "index": part["index"]},
                        "reason": "Part has a restricted suffix.",
                    }
                )
            elif action == "clean":
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "SUFFIX",
                        "subtype": "REMOVE",
                        "priority": 3,
                        "details": {"part": part["part"], "index": part["index"]},
                        "reason": "Removed part due to restricted suffix.",
                    },
                    priority=3
                )

    def process_restricted_prefixes(self, part: dict, action: str):
        """Process restricted Egnyte prefixes."""
        if any(part["part"].lower().startswith(prefix) for prefix in self.starts):
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "PREFIX",
                        "details": {"part": part["part"], "index": part["index"]},
                        "reason": "Part has a restricted prefix.",
                    }
                )
            elif action == "clean":
                cleaned_part = part["part"]
                for prefix in self.starts:
                    if cleaned_part.lower().startswith(prefix):
                        cleaned_part = cleaned_part[len(prefix):]
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "PREFIX",
                        "subtype": "MODIFY",
                        "priority": 3,
                        "details": {"original": part["part"], "new_value": cleaned_part, "index": part["index"]},
                        "reason": "Removed restricted prefix from part.",
                    },
                    priority=3
                )

    def process_temp_patterns(self, part: dict, action: str):
        """Process restricted temporary file patterns."""
        if any(re.match(pattern, part["part"].lower()) for pattern in self.temp_patterns):
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "TEMP_PATTERN",
                        "details": {"part": part["part"], "index": part["index"]},
                        "reason": "Part matches a restricted temporary file pattern.",
                    }
                )
            elif action == "clean":
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "TEMP_PATTERN",
                        "subtype": "REMOVE",
                        "priority": 4,
                        "details": {"part": part["part"], "index": part["index"]},
                        "reason": "Removed part due to restricted temporary file pattern.",
                    },
                    priority=4
                )

    def process_part_length(self, part: dict, action: str):
        """Process part length based on Egnyte's restrictions."""
        if len(part["part"]) > self.part_length:
            if action == "validate":
                self._path_helper.add_issue(
                    {
                        "type": "issue",
                        "category": "PART_LENGTH",
                        "details": {"part": part["part"], "index": part["index"]},
                        "reason": f"Part exceeds maximum length of {self.part_length} characters.",
                    }
                )
            elif action == "clean":
                truncated_part = part["part"][:self.part_length]
                self._path_helper.add_action(
                    {
                        "type": "action",
                        "category": "PART_LENGTH",
                        "subtype": "MODIFY",
                        "priority": 2,
                        "details": {"original": part["part"], "new_value": truncated_part, "index": part["index"]},
                        "reason": f"Truncated part to meet length requirements.",
                    },
                    priority=2
                )
