import re

class BaseService:
    # Default invalid characters
    invalid_characters = '<>:"|?*'
    max_length = 255  # Default maximum length

    def __init__(self, path: str, auto_clean: bool = False):
        self.original_path = path  # Store the original unmodified path
        self.path = path.replace("\\", "/")
        self.path = f"/{self.path}" if not self.path.startswith("/") else self.path
        self.path_length = len(self.path)
        self.path_parts = self.path.strip("/").split('/') if '/' in self.path else [self.path]
        self.filename = self.path_parts[-1]
        self.filename_ext = self.filename.split('.')[-1] if '.' in self.filename else ''
        self.restricted_names = set()
        
        # Clean the path if the auto_clean flag is set
        if auto_clean:
            self.path = self.get_cleaned_path()
    
    @staticmethod
    def path_part_contains_invalid_characters(part):
        invalid_pattern = re.compile(f"[{re.escape(BaseService.invalid_characters)}]")
        return re.search(invalid_pattern, part)

    def check_path_length(self):
        """Check if the path length exceeds the maximum allowed."""
        if self.path_length > self.max_length:
            raise ValueError(
                f"The specified path is too long. "
                f"Current length: {self.path_length} characters. "
                f"Maximum allowed length is {self.max_length} characters."
            )
    def check_invalid_character(self, part):
        """Check for invalid characters in a part."""
        invalid_character = self.path_part_contains_invalid_characters(part)
        if invalid_character:
            raise ValueError(
                f'Invalid character "{invalid_character.group()}" found in: "{part}". '
                f'Please avoid using: {self.invalid_characters}'
            )

    def check_leading_trailing_spaces(self, part):
        """Check for leading or trailing spaces in a part."""
        if part != part.strip():
            raise ValueError(f'Leading or trailing spaces are not allowed in: "{part}".')

    def check_if_valid_folder(self, part):
        """Perform folder-specific checks."""
        self.check_invalid_character(part)
        self.check_leading_trailing_spaces(part)
        if part.endswith("."):
            raise ValueError(f'Folder names cannot end with a period: "{part}".')

    def check_if_valid_filename(self, filename):
        """Perform filename-specific checks."""
        if '.' not in filename:
            raise ValueError(f'Filename "{filename}" must contain an extension.')
        self.check_leading_trailing_spaces(filename)
        self.check_invalid_character(filename)

    # strict validation checking by default. 
    # if you want to check only the cleaned path, set clean_only=True :) 
    def check_if_valid(self, clean_only: bool = False):
        """Validate the path parts, with an option to check only the cleaned path."""
        if clean_only:
            # Validate based on cleaned path
            cleaned_path = self.get_cleaned_path()
            if len(cleaned_path) > self.max_length:
                raise ValueError(
                    f"Cleaned path is too long. Current length: {len(cleaned_path)} characters. "
                    f"Maximum allowed length is {self.max_length} characters."
                )
            for part in cleaned_path.strip("/").split('/'):
                self.check_if_valid_folder(part)  # Validate each part of the cleaned path
        else:
            self.check_path_length()  # Use the overridden value if in a subclass
            for idx, part in enumerate(self.path_parts):
                if idx < len(self.path_parts) - 1:  # All but the last part are folders
                    self.check_if_valid_folder(part)
                else:  # Last part is the filename
                    self.check_if_valid_filename(part)

        return True
    
    @staticmethod
    def truncate_filepath(path: str, max_length: int = 255):
        path_length = len(path)
        if path_length <= max_length:
            return path
        path_parts = path.strip("/").split('/') if '/' in path else [path]
        filename = path_parts[-1]
        path_up_to_filename = '/'.join(path_parts[:-1])
        filename_length = len(filename)
        if path_length <= max_length:
            return path
        path_up_to_filename = '/'.join(path_parts[:-1])
        filename_length = len(filename)
        num_of_chars_we_can_use = max_length - (filename_length + 1)
        if num_of_chars_we_can_use < 0:
            raise ValueError(f"Filename is too long to fit in the path: {filename}")
        truncated_path = f"{path_up_to_filename[:num_of_chars_we_can_use]}/{filename}"
        return truncated_path

    def get_cleaned_path(self, raise_error: bool = True):
        """Clean the path and return the cleaned path."""
        path = self.path
        path = ''.join([char for char in path if char not in self.invalid_characters])  # Remove invalid characters
        path_parts = path.strip("/").split('/') if '/' in path else [path]
        # Clean the path parts and handle filename normalization here
        cleaned_parts = []
        for part in path_parts:
            if '.' in cleaned_part:
                name_part, ext_part = cleaned_part.rsplit('.', 1)
                cleaned_part = f"{name_part.strip()}.{ext_part.strip()}" if ext_part else name_part.strip()
                        
            # remove restricted names from the path
            for restricted_name in self.restricted_names:
                if restricted_name in cleaned_part:
                    part = part.replace(restricted_name, "")

            part = part.strip().rstrip(".")
            if not part:
                continue
            cleaned_parts.append(part)

        output_path = '/'.join([s for s in cleaned_parts if s])  # Join the cleaned parts
        output_path = output_path.strip("/")
        output_path = f"/{output_path}" if not output_path.startswith("/") else output_path

        output_path = BaseService.truncate_filepath(output_path, self.max_length)

        # Optionally check if the cleaned path is valid
        cleaned_path_instance = BaseService(output_path)
        if raise_error:
            cleaned_path_instance.check_if_valid()

        return cleaned_path_instance.path

