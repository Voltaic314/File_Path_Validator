import re


class BaseService:
    # This will be overridden in subclasses
    invalid_characters = ""

    # Set default maximum length for paths
    max_length = 255  # Default for Windows, can be overridden in subclasses

    def __init__(self, path: str):
        self.path = path.strip().replace("\\", "/")  # Normalize the path
        self.path = f"/{self.path}" if not self.path.startswith("/") else self.path # this is more so to help with the split logic portions so that the first part is always the root. It also helps prevent split errors if the path is just a filename for example (or empty).
        self.path_length = len(self.path)
        self.path_parts = self.path.strip("/").split('/') if '/' in self.path else [self.path]
        self.filename = self.path_parts[-1] if self.path_parts else self.path

    @staticmethod
    def path_part_contains_invalid_characters(part):
        invalid_pattern = re.compile(f"[{re.escape(BaseService.invalid_characters)}]")
        return re.search(invalid_pattern, part)

    def check_if_valid(self):
        # List of restricted names can be customized per service
        RESTRICTED_NAMES = set()
        RESTRICTED_PREFIX = ""
        
        if self.path_length > self.max_length:
            raise ValueError(
                f"The specified path is too long. "
                f"Current length: {self.path_length} characters. "
                f"Maximum allowed length is {self.max_length} characters."
            )

        for part in self.path_parts:
            # Check for invalid characters
            invalid_character = self.path_part_contains_invalid_characters(part)
            if invalid_character:
                raise ValueError(
                    f"Invalid character \"{invalid_character.group()}\" found in this section of the proposed file path: \"{part}\". "
                    f"Please make sure the file path does not contain any of the following characters: {self.invalid_characters}"
                )
            
            # Check for restricted names
            if part in RESTRICTED_NAMES:
                raise ValueError(f"Restricted name found in path: \"{part}\"")

            # Check for leading or trailing spaces
            if part != part.strip():
                raise ValueError(f"Leading or trailing spaces found in path: \"{part}\"")

            # Check for restricted prefixes
            if part.startswith(RESTRICTED_PREFIX):
                raise ValueError(f"Restricted prefix found in path: \"{part}\"")
        
        return True

    def get_cleaned_path(self):
        return '/'.join([s.strip() for s in self.path_parts if s.strip()])
