from FPV.Helpers._base import FPV_Base


class FPV_ShareFile(FPV_Base):
    # Invalid characters specific to ShareFile
    invalid_characters = ':;*?"<>~'
    max_length = 255  # ShareFile has a maximum path length of 255 characters
    acceptable_root_patterns = []

    def __init__(self, path, **kwargs):
        kwargs.pop("relative", None)  # Remove relative argument
        super().__init__(path, relative=True, **kwargs)

    def processing_methods(self):
        """Define the processing methods for ShareFile paths."""
        return {
            "root": [],
            "folder": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_trailing_periods(part, action),
                lambda part, action: self.process_empty_parts(part, action),
                lambda part, action: self.process_path_length(part, action),
            ],
            "file": [
                lambda part, action: self.process_invalid_characters(part, action),
                lambda part, action: self.process_whitespace(part, action),
                lambda part, action: self.process_trailing_periods(part, action),
                lambda part, action: self.process_path_length(part, action),
            ],
        }
