import re
from Helpers._base_service import BaseService

class Egnyte(BaseService):
    # Invalid characters for Egnyte file and folder names
    invalid_characters = '\\/":<>|*?'

    def __init__(self, path: str):
        super().__init__(path)
        
        # Store the original path
        self.original_path = path
        
        # Handle filename and extension
        self.filename = self.path_parts[-1] if self.path_parts else self.path
        self.filename_ext = self.filename.split('.')[-1]

    @staticmethod
    def path_part_contains_invalid_characters(part):
        invalid_pattern = re.compile(f"[{re.escape(Egnyte.invalid_characters)}]")
        return re.search(invalid_pattern, part)

    def check_if_valid(self):
        # List of restricted names and suffixes
        RESTRICTED_NAMES = {
            ".ds_store", ".metadata_never_index", ".thumbs.db", "powerpoint temp", "desktop.ini", "icon\r"
        }
        ENDINGS = ['.', '~', '._attribs_', '._rights_', '._egn_', '_egnmeta', '.tmp', '-spotlight', '.ac$', '.sv$', '.~vsdx']
        STARTS = ['._', '.~', 'word work file', '_egn_.', '.smbdelete']
        STARTS_WITH_TILDE_ENDINGS = ['.idlk', '.xlsx', '.xlsx (deleted)', '.pptx', '.pptx (deleted)']
        STARTS_WITH_TILDE_DOLLAR_ENDINGS = ['.doc', '.docx', '.docx (deleted)', '.rtf', '.ppt', '.pptx', '.pptx (deleted)', '.xlsm', '.xlsm (deleted)', '.sldlfp', '.slddrw', '.sldprt', '.sldasm']
        RESTRICTED_FOLDER_NAMES = {'.data', '.tmp'}
        RESTRICTED_FOLDER_PREFIXES = ['.spotlight-']

        # Overall path length limitation
        if self.path_length > 5000:
            raise ValueError(
                f"The specified path is too long. Current length: {self.path_length} characters. Maximum allowed length is 5000 characters."
            )

        # Check each part of the path
        for idx, part in enumerate(self.path_parts):
            is_last_part = (idx == len(self.path_parts) - 1)
            is_folder = not is_last_part

            # Check for invalid characters
            invalid_character = Egnyte.path_part_contains_invalid_characters(part)
            if invalid_character:
                raise ValueError(
                    f"Invalid character \"{invalid_character.group()}\" found in: \"{part}\". "
                    f"Please avoid using: {Egnyte.invalid_characters} in the file path."
                )
            
            # Check for leading or trailing spaces
            if part != part.strip():
                raise ValueError(f"Leading or trailing spaces found in: \"{part}\"")

            # Check for parts that end with period(s)
            if part.rstrip('.') != part:
                raise ValueError(f"Part ends with period(s): \"{part}\"")

            # Check for control characters
            for c in part:
                if ord(c) < 32 or ord(c) == 127:
                    raise ValueError(f"Control character found in: \"{part}\"")

            # Check for Unicode characters with 4 or more bytes
            for c in part:
                if len(c.encode('utf-8')) >= 4:
                    raise ValueError(f"Character requiring 4+ bytes in UTF-8 found in: \"{part}\"")

            # Check for component length
            if len(part) > 245:  # Folder name length limit
                raise ValueError(f"Path component exceeds 245 characters: \"{part}\"")

            # Check for restricted names
            if part.lower() in RESTRICTED_NAMES:
                raise ValueError(f"Restricted name found: \"{part}\"")

            # Check for names ending with restricted suffixes
            for ending in ENDINGS:
                if part.lower().endswith(ending):
                    raise ValueError(f"Name ends with restricted suffix \"{ending}\": \"{part}\"")

            # Check for names starting with restricted prefixes
            for start in STARTS:
                if part.lower().startswith(start):
                    raise ValueError(f"Name starts with restricted prefix \"{start}\": \"{part}\"")

            # Check for names starting with '~' and ending with certain extensions
            if part.startswith('~'):
                for ending in STARTS_WITH_TILDE_ENDINGS:
                    if part.endswith(ending):
                        raise ValueError(f"Name starts with '~' and ends with \"{ending}\": \"{part}\"")

            # Check for names starting with '~$' and ending with certain extensions
            if part.startswith('~$'):
                for ending in STARTS_WITH_TILDE_DOLLAR_ENDINGS:
                    if part.endswith(ending):
                        raise ValueError(f"Name starts with '~$' and ends with \"{ending}\": \"{part}\"")

            # Check for AutoCAD temp files starting with 'atmp' and ending with four numbers
            if re.match(r'^atmp\d{4}$', part.lower()):
                raise ValueError(f"AutoCAD temp file detected: \"{part}\"")

            # Check for SAS temp files ending in '.sas.b' followed by two numbers
            if re.match(r'.*\.sas\.b\d{2}$', part.lower()):
                raise ValueError(f"SAS temp file detected: \"{part}\"")

            # Check for PDF temp files starting with 'aa' followed by a single letter and five numbers
            if re.match(r'^aa[a-zA-Z]\d{5}$', part.lower()):
                raise ValueError(f"PDF temp file detected: \"{part}\"")

            # Check for names ending with '.$$$'
            if part.lower().endswith('.$$$'):
                raise ValueError(f"File ending with '.$$$' detected: \"{part}\"")

            # Folder specific checks
            if is_folder:
                # Check for restricted folder names
                if part.lower() in RESTRICTED_FOLDER_NAMES:
                    raise ValueError(f"Restricted folder name found: \"{part}\"")
                # Check for restricted folder prefixes
                for prefix in RESTRICTED_FOLDER_PREFIXES:
                    if part.lower().startswith(prefix):
                        raise ValueError(f"Folder name starts with restricted prefix \"{prefix}\": \"{part}\"")

        return True

    def get_cleaned_path(self):
        """
        Returns a cleaner version of the file path that is stripped out of excess white spaces
        """
        path = '/'.join([part.strip() for part in self.path_parts if part.strip()])
        if not path.startswith("/"):
            path = "/" + path
        return path
