from FPV.Helpers._base import FPV_Base


class FPV_Dropbox(FPV_Base):
    # Dropbox-specific rules
    invalid_characters = '<>:"|?*.'
    max_length = 260
    restricted_names = {
        ".lock", "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", 
        "COM6", "COM7", "COM8", "COM9", "LPT1", 
        "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", 
        "LPT7", "LPT8", "LPT9"
    }
    acceptable_root_patterns = [r"^/$", r"^/root$"]

    def __init__(self, path, **kwargs):
        sep = kwargs.get("sep", "/")  # Default separator is "/"
        # Check if the first part of the path is explicitly "root"
        if path.split(sep)[0] != "root" if path.split(sep) else True:
            kwargs.pop("relative", None)  # Remove relative argument
            super().__init__(path, relative=True, **kwargs)
        else:
            super().__init__(path, **kwargs)

    # this is to get around weird quirks where 
    # dropbos will yell at you for having a "." in a file name which 
    # doesn't make any sense lol.
    def process_invalid_characters(self, part, action):
        if part.get("is_file", False):
            self.invalid_characters = self.invalid_characters.replace(".", "")
        cleaned_part = super().process_invalid_characters(part, action) # if action is clean that is
        self.invalid_characters = '<>:"|?*.'  # Reset invalid characters
        return cleaned_part

    def processing_methods(self):
        """Define the processing methods for Dropbox paths."""
        return {
            "root": [],
            "folder": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_path_length(part, action),
            ],
            "file": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_path_length(part, action),
            ],
        }
