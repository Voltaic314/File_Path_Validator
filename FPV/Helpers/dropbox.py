from FPV.Helpers._base_service import BaseService

class Dropbox(BaseService):
    # Dropbox has a maximum path length of 260 characters
    max_length = 260

    def __init__(self, path: str):
        super().__init__(path)  # Call the base class constructor

    def check_if_valid(self):
        # Call the base class check for path length and general validation
        super().check_if_valid()  

        # Specific checks for Dropbox
        # Check for restricted names
        self.RESTRICTED_NAMES = {
            ".lock", "CON", "PRN", "AUX", "NUL", 
            "COM0", "COM1", "COM2", "COM3", "COM4", 
            "COM5", "COM6", "COM7", "COM8", "COM9", 
            "LPT0", "LPT1", "LPT2", "LPT3", "LPT4", 
            "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        }
        for part in self.path_parts:
            # Check for restricted names
            if part in self.RESTRICTED_NAMES:
                raise ValueError(f'Restricted name found in path: "{part}"')
            
        return True
    
    def get_cleaned_path(self, raise_error: bool = True):
        cleaned_path = super().get_cleaned_path(raise_error)
        
        cleaned_path_parts = []
        for part in cleaned_path.split("/"):

            # check for restricted names
            for restricted_name in self.RESTRICTED_NAMES:
                part = part.replace(restricted_name, "")

            part = part.strip().rstrip(".")

            if not part:
                continue 
            
            cleaned_path_parts.append(part)
        

        output_path = '/'.join(cleaned_path_parts)
        output_path = output_path.strip('/')
        output_path = f'{"/" + output_path}' if not output_path.startswith("/") else output_path

        cleaned_path_instance = Dropbox(output_path)
        if raise_error:
            cleaned_path_instance.check_if_valid()
        
        return cleaned_path_instance.path
