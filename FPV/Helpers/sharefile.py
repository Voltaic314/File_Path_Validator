from FPV.Helpers._base_service import BaseService

class ShareFile(BaseService):
    # Invalid characters for ShareFile file and folder names
    invalid_characters = ':;*?"<>~'

    def __init__(self, path: str):
        super().__init__(path)  # Call the base class constructor

    def check_if_valid(self):
        # Override the invalid characters for ShareFile
        self.invalid_characters = ShareFile.invalid_characters

        # Call the base class check for general validation and path length
        super().check_if_valid()
        
        return True
