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
    
    def get_cleaned_path(self, raise_error: bool = True):
        cleaned_path = super().get_cleaned_path(raise_error)
        
        cleaned_path_parts = []
        for part in cleaned_path.split("/"):
            for char in self.invalid_characters:
                part = part.replace(char, "")

            
            part = part.strip().rstrip(".")
            
            if not part:
                continue
            
            cleaned_path_parts.append(part)
        
        output_path = '/'.join(cleaned_path_parts)
        output_path = output_path.strip('/')
        output_path = f'{"/" + output_path}' if not output_path.startswith("/") else output_path

        cleaned_path_instance = ShareFile(output_path)
        if raise_error:
            cleaned_path_instance.check_if_valid()
        
        return cleaned_path_instance.path
    