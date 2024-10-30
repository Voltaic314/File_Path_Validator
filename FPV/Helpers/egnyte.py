import re
from FPV.Helpers._base_service import BaseService


class Egnyte(BaseService):
    # Egnyte-specific character restrictions
    invalid_characters = ':*?"<>|'
    max_length = 5000  # Max path length
    part_length = 245  # Max length per path part

    def __init__(self, path, auto_clean=False, relative=True):
        super().__init__(path, auto_clean=auto_clean, relative=relative)

        # Define Egnyte-specific restricted names, suffixes, prefixes
        self.restricted_names = {
            ".ds_store", ".metadata_never_index", ".thumbs.db",
            "powerpoint temp", "desktop.ini", "icon\r", ".data", ".tmp"
        }
        self.endings = [
            ".", "~", "._attribs_", "._rights_", "._egn_", "_egnmeta",
            ".tmp", "-spotlight", ".ac$", ".sv$", ".~vsdx"
        ]
        self.starts = ["._", ".~", "word work file", "_egn_.", ".smbdelete", ".spotlight-"]
        self.starts_with_tilde_endings = [".idlk", ".xlsx", ".pptx"]
        self.starts_with_tilde_dollar_endings = [
            ".doc", ".docx", ".rtf", ".ppt", ".pptx", 
            ".xlsm", ".sldlfp", ".slddrw", ".sldprt", ".sldasm"
        ]
        self.temp_patterns = [
            r"^atmp\d{4}$",  # AutoCAD temp files, e.g., "atmp3829"
            r"^.+\.sas\.b\d{2}$",  # SAS temp files, e.g., "myFile.sas.b73"
            r"^aa[a-zA-Z]\d{5}$",  # PDF temp files, e.g., "aau38221"
            r"^.+\.\$\$\$$"  # Files ending in .$$$, e.g., "myFile.$$$"
        ]

        # Update validation and cleaning methods for Egnyte-specific needs
        self.corresponding_validate_and_clean_methods.update({
            "part_length": {"validate": "validate_part_length", "clean": "truncate_part_length"},
            "suffixes": {"validate": "validate_suffixes", "clean": "remove_restricted_suffixes"},
            "prefixes": {"validate": "validate_prefixes", "clean": "remove_restricted_prefixes"},
            "temp_patterns": {"validate": "validate_temp_patterns", "clean": "remove_temp_patterns"}
        })

    def validate(self):
        """Validate the path according to Egnyte-specific rules."""
        self.validate_path_length()
        self.validate_part_length()
        self.validate_restricted_names()
        self.validate_if_whitespace_around_parts()

        for part in self.path_parts:
            self.validate_suffixes(part)
            self.validate_prefixes(part)
            self.validate_temp_patterns(part)

        self.validate_empty_parts()

    def clean(self, raise_error=True):
        """Clean and return an Egnyte-compliant path; validate if raise_error is True."""
        cleaned_path = self.path
        cleaned_path = self.clean_and_validate_path("path_length", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("part_length", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("invalid_characters", path=cleaned_path)

        cleaned_path_parts = []
        for part in cleaned_path.split('/'):
            part = self.remove_restricted_suffixes(part)
            part = self.remove_restricted_prefixes(part)
            part = self.remove_temp_patterns(part)
            part = part.strip().rstrip(".")

            if part:
                cleaned_path_parts.append(part)

        cleaned_path = self.clean_and_validate_path("restricted_names", path=cleaned_path)

        cleaned_path = '/'.join(cleaned_path_parts).strip('/')
        cleaned_path = f"/{cleaned_path}" if not cleaned_path.startswith("/") else cleaned_path

        # Revalidate cleaned path if needed
        if raise_error:
            cleaned_path_instance = Egnyte(cleaned_path, auto_clean=False, relative=self.relative)
            cleaned_path_instance.validate()

        return cleaned_path

    # Egnyte-specific helper methods
    def validate_part_length(self):
        """Validate each part's length for Egnyte (max 245 characters)."""
        for part in self.path_parts:
            if len(part) > self.part_length:
                raise ValueError(f"Path component exceeds 245 characters: '{part}'")
            
    def truncate_part_length(self, part):
        """Truncate each part to 245 characters."""
        return part[:self.part_length] if len(part) > self.part_length else part

    def validate_suffixes(self, part):
        """Validate that no part ends with restricted Egnyte suffixes."""
        for suffix in self.endings:
            if part.lower().endswith(suffix):
                raise ValueError(f"Path component '{part}' has restricted suffix: '{suffix}'")

    def validate_prefixes(self, part):
        """Validate that no part starts with restricted Egnyte prefixes."""
        while any(part.lower().startswith(prefix) for prefix in self.starts):
            for prefix in self.starts:
                if part.lower().startswith(prefix):
                    raise ValueError(f"Path component '{part}' has restricted prefix: '{prefix}'")

        if part.startswith("~$"):
            for ending in self.starts_with_tilde_dollar_endings:
                if part.endswith(ending):
                    raise ValueError(f"Path component '{part}' starts with '~$' and ends with '{ending}'")
        elif part.startswith("~"):
            for ending in self.starts_with_tilde_endings:
                if part.endswith(ending):
                    raise ValueError(f"Path component '{part}' starts with '~' and ends with '{ending}'")

    def validate_temp_patterns(self, part):
        """Validate against specific temporary file patterns unique to Egnyte."""
        for pattern in self.temp_patterns:
            if re.match(pattern, part.lower()):
                raise ValueError(f"Path component '{part}' matches restricted temporary file pattern.")

    def remove_restricted_suffixes(self, part):
        """Remove restricted Egnyte suffixes from a path part."""
        for suffix in self.endings:
            if part.lower().endswith(suffix):
                part = "" # Remove the whole part if it ends with a restricted suffix
        return part

    def remove_restricted_prefixes(self, part):
        """Remove all restricted Egnyte prefixes from a path part."""
        while any(part.lower().startswith(prefix) for prefix in self.starts):
            for prefix in self.starts:
                if part.lower().startswith(prefix):
                    part = part[len(prefix):]  # Remove the matching prefix

        if part.startswith("~$"):
            part = part[2:]  # Remove leading '~$'
        elif part.startswith("~"):
            part = part[1:]  # Remove leading '~'

        return part

    def remove_temp_patterns(self, part):
        """Remove components matching Egnyte's restricted temporary file patterns."""
        for pattern in self.temp_patterns:
            if re.match(pattern, part.lower()):
                return ""  # Remove the whole part if it matches a temp pattern
        return part

if __name__ == "__main__":
    path = "._ds_store/temp_folder_name_with_~$file.docx/invalid|chars.tmp"
    egnyte = Egnyte(path)
    egnyte.max_length = 5000
    egnyte.part_length = 245
    cleaned_path = egnyte.clean()
    print(f"Original path: {path}\nCleaned path: {cleaned_path}")