from FPV.Helpers._base import FPV_Base


class FPV_Box(FPV_Base):
    # Box-specific invalid characters, maximum length, and restricted names
    invalid_characters = '<>:"|?*'
    max_length = 255
    restricted_names = {
        "outlook.pst", "quickbooks.qbb", "google_docs.gdoc", 
        "google_sheets.gsheet", "google_slides.gslides", "mac_package.pkg"
    }
    acceptable_root_patterns = [
        r"^root$",  # Explicit root folder named "root" (internal representation)
    ]

    def __init__(self, path, **kwargs):
        sep = kwargs.get("sep", "/")  # Default separator is "/"
        # Check if the first part of the path is explicitly "root"
        if path.split(sep)[0] != "root" if path.split(sep) else True:
            kwargs.pop("relative", None)  # Remove relative argument
            super().__init__(path, relative=True, **kwargs)
        else:
            super().__init__(path, **kwargs)

    def processing_methods(self):
        """Define the processing methods for Box paths."""
        return {
            "root": [],
            "folder": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_trailing_periods(part, action),
                lambda part, action: self.process_path_length(part, action),
            ],
            "file": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_restricted_names(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_trailing_periods(part, action),
                lambda part, action: self.process_path_length(part, action),
            ],
        }
