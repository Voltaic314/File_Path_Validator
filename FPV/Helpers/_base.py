import re
from typing import List

class FPV_Base:
    """Base class for path validation and cleaning."""
    
    # helpers 
    @staticmethod
    def normalize_path(path: str, relative: bool = True, sep='/') -> str:
        """Normalize the path by replacing backslashes with forward slashes and ensuring it starts with a slash."""
        path = path.replace("\\", sep).replace("/", sep) # replace all slashes with the sep slashes
        if not path.startswith(sep):
            path = f"{sep}{path}" if relative else f"{path}"
        return path
    
    @staticmethod
    def get_path_parts(path: str, sep='/') -> list:
        """Get the parts of the path by splitting on forward slashes."""
        return path.strip(sep).split(sep) if sep in path else [path]

    # Default invalid characters
    invalid_characters = ''
    max_length = 0  # Default maximum length
    restricted_names: set = set()

    corresponding_validate_and_clean_methods  = {
        "path_length": {"validate": "validate_path_length", "clean": "truncate_path"},
        "restricted_names": {"validate": "validate_restricted_names", "clean": "remove_restricted_names"},
        "part_ends_with_period": {"validate": "validate_if_part_ends_with_period", "clean": "remove_trailing_periods"},
        "whitespace_around_parts": {"validate": "validate_if_whitespace_around_parts", "clean": "remove_whitespace_around_parts"},
        "empty_parts": {"validate": "validate_empty_parts", "clean": "remove_empty_parts"},
        "invalid_characters": {"validate": "validate_invalid_characters", "clean": "remove_invalid_characters"},
        "_main": {"validate": "validate", "clean": "clean"}
    }

    def __init__(self, path: str, auto_clean: bool = False, relative: bool = True, check_folders=True, check_files=True, sep='/'):
        self.original_path: str = path
        self.sep: str = sep
        self.path: str = FPV_Base.normalize_path(path, relative, sep=self.sep)
        self.path_parts: List[str] = FPV_Base.get_path_parts(self.path) 
        self.relative: bool = relative
        self.check_folders: bool = check_folders
        self.check_files: bool = check_files
        self.auto_clean: bool = auto_clean
        self.init_kwargs = {
            "auto_clean": self.auto_clean,
            "relative": self.relative,
            "check_folders": self.check_folders,
            "check_files": self.check_files,
            "sep": self.sep
        }

        if self.auto_clean:
            self.path = self.clean()

    def get_validate_or_clean_method(self, method: str, action: str, **kwargs):
        """
        The purpose of this method is to return the appropriate 
        validate or clean method based on the method and action passed.
        If you pass in "clean" as your action argument then you need to also pass in the "path" argument.

        Args:
            method (str): The name of the validate/clean method pair to use.
            action (str): The action to perform, either "validate" or "clean".
            **kwargs: Additional keyword arguments to pass to the method.

        Returns:
        if action == "validate":
            bool: The result of the validation.
        elif action == "clean":
            str: The cleaned path.
        """
        return getattr(self, self.corresponding_validate_and_clean_methods[method][action], **kwargs)
    
    def clean_and_validate_path(self, method: str, raise_error: bool = False, **kwargs):
        """
        Clean the path with the specified clean method, then optionally validate.
        
        Args:
            method (str): The name of the validate/clean method pair to use.
            raise_error (bool): Whether to raise an error if the cleaned path is still invalid.

        Returns:
            str: The cleaned path.
        """
        # Call the clean method
        clean_method = self.get_validate_or_clean_method(method, "clean")
        cleaned_path = clean_method(**kwargs)

        # If raise_error is set, validate the cleaned path
        if raise_error:
            # Create a new instance of the current class with the cleaned path
            cleaned_instance = self.__class__(path=cleaned_path, **self.init_kwargs)
            # should we call the specific validate method or validate the whole thing? 
            # Hmm....... I guess we'll just validate the whole thing for now.
            validate_method = self.get_validate_or_clean_method(method, "validate")
            cleaned_instance.validate()

        return cleaned_path

    def path_part_contains_invalid_characters(self, part):
        invalid_pattern = re.compile(f"[{re.escape(self.invalid_characters)}]")
        return re.search(invalid_pattern, part)

    def validate_invalid_characters(self, path=''):
        """Validate for invalid characters in each part of the path and report specific invalid characters."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        for index, part in enumerate(input_path_parts):
            # if not relative and current windows in current class name.lower() then skip the first part.
            if not self.relative and "windows" in self.__class__.__name__.lower():
                if index == 0:
                    continue # this is handled in the windows sub class but it gives false positives here if this isn't here.
            match = self.path_part_contains_invalid_characters(part)
            if match:
                raise ValueError(
                    f'Invalid character "{match.group()}" found in part: "{part}". '
                    f'Please ensure the path does not contain any of the following characters: {self.invalid_characters}'
                )

    def remove_invalid_characters(self, path=''):
        """Remove invalid characters from each part of the path and return the cleaned path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        cleaned_parts = []
        for index, part in enumerate(input_path_parts):

            # this is some ugly hard coded bullshit if I'm being honest lol
            if not self.relative and "windows" in self.__class__.__name__.lower():
                if index == 0:
                    self.invalid_characters = self.invalid_characters.replace(":", "")
                else:
                    self.invalid_characters = self.invalid_characters + ':' if ':' not in self.invalid_characters else self.invalid_characters
            
            cleaned_part = re.sub(f"[{re.escape(self.invalid_characters)}]", "", part)
            if cleaned_part:  # Only add non-empty parts
                cleaned_parts.append(cleaned_part)
        output_path = self.sep.join(cleaned_parts)
        return output_path

    def validate_path_length(self, path=''):
        """validate if the path length exceeds the maximum allowed."""
        input_path = self.path if not path else path
        if self.max_length and len(input_path) > self.max_length:
            raise ValueError(f"The specified path is too long. Maximum allowed is {self.max_length} characters.")

    def truncate_path(self, path='', check_files=True):
        """Truncate the path length to meet the maximum length requirement."""
        input_path = self.path if not path else path
        if len(input_path) <= self.max_length:
            return input_path
        
        # Use as much of the filename as possible but raise if the filename alone exceeds max length
        if check_files:
            filename = input_path.split(self.sep)[-1]
            filename_length = len(filename)
            if filename_length > self.max_length:
                raise ValueError(f"The filename is too long. Maximum allowed is {self.max_length} characters.")

            # Calculate maximum usable path length minus filename
            max_path_length = self.max_length - filename_length - 1
            truncated_path = path[:max_path_length]
            
            return f"{self.sep}{truncated_path.strip(self.sep)}{self.sep}{filename.strip(self.sep)}"
        else:
            # just truncate it to the max length after stripping for / signs
            return f"{self.sep}{input_path.strip(self.sep)[:self.max_length]}"

    def validate_restricted_names(self, path=''):
        """validate for restricted names in each part of the path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        for part in input_path_parts:
            if part.lower() in [s.lower() for s in self.restricted_names]:
                raise ValueError(f'Restricted name "{part}" found in path.')

    def remove_restricted_names(self, path=''):
        """Remove restricted names from each part of the path and return the cleaned path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        cleaned_parts = [part for part in input_path_parts if part not in self.restricted_names]
        ouput_path = self.sep.join(cleaned_parts)
        return ouput_path

    def validate_if_part_ends_with_period(self, path=''):
        """validate if any part of the path ends with a period."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        for part in input_path_parts:
            if part.endswith('.'):
                raise ValueError(f'"{part}" cannot end with a period.')

    def remove_trailing_periods(self, path=''):
        """Remove trailing periods from each part of the path and return the cleaned path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        cleaned_parts = [part.rstrip('.') for part in input_path_parts if part.rstrip('.')]
        return self.sep.join(cleaned_parts)

    def validate_if_whitespace_around_parts(self, path=''):
        """validate if there are leading or trailing spaces in any part of the path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        for index, part in enumerate(input_path_parts):
            if part != part.strip():
                raise ValueError(f'Leading or trailing spaces are not allowed in: "{part}".')
            check_files_true = index == len(input_path_parts) - 1 and self.check_files
            if '.' in part and check_files_true:
                for period_part in part.split('.'):
                    if period_part != period_part.strip():
                        raise ValueError(f'Leading or trailing spaces are not allowed in: "{period_part}".')
    
    def remove_whitespace_around_parts(self, path=''):
        """Remove leading and trailing spaces from each part of the path and return the cleaned path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        cleaned_parts = []
        for index, part in enumerate(input_path_parts):
            part = part.strip()
            if '.' in part and self.check_files and index == len(input_path_parts) - 1:
                before, after = part.split('.')
                part = f"{before.strip()}.{after.strip()}"
            cleaned_parts.append(part)
        return self.sep.join(cleaned_parts)
                    
    def remove_whitespace_around_part(self, part='', is_file=False):
        """Remove leading and trailing spaces from each part of the path and return the cleaned path."""
        if '.' in part and is_file:
            before, after = part.split('.')
            part = f"{before.strip()}.{after.strip()}"
        return part.strip()

    def validate_empty_parts(self, path=''):
        """validate for empty parts in the path."""
        input_path = self.path if not path else path
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        if '' in input_path_parts:
            raise ValueError('Empty parts are not allowed in the path.')

    def remove_empty_parts(self, path=''):
        """Remove any empty parts in the path and return the cleaned path."""
        input_path_parts = self.path_parts if not path else FPV_Base.get_path_parts(path, sep=self.sep)
        cleaned_parts = [part for part in input_path_parts if part]
        output_path = self.sep.join(cleaned_parts)
        return output_path

    def validate(self, path=''):
        return True

    def clean(self, raise_error=True, path=''):
        return self.path
