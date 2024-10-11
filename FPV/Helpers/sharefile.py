import re
from FPV.Helpers._base_service import BaseService

class ShareFile(BaseService):
    # Invalid characters for ShareFile file and folder names
    invalid_characters = ':;*?"<>~'

    @staticmethod
    def path_part_contains_invalid_characters(part):
        invalid_pattern = re.compile(f"[{re.escape(ShareFile.invalid_characters)}]")
        return re.search(invalid_pattern, part)
    

    def __init__(self, path: str):
        super().__init__(path)  # Call the base class constructor

    def check_if_valid(self):

        # Call the base class check for general validation and path length
        super().check_if_valid()
        
        # invalid char check
        for part in self.path_parts:
            invalid_character = ShareFile.path_part_contains_invalid_characters(part)
            if invalid_character:
                raise ValueError(
                    f'Invalid character "{invalid_character.group()}" found in this section of the proposed file path: "{part}". '
                    f'Please make sure the file path does not contain any of the following characters: {ShareFile.invalid_characters}'
                )

        return True
    