from Helpers.box import Box
from Helpers.dropbox import Dropbox
from Helpers.egnyte import Egnyte
from Helpers.onedrive import OneDrive
from Helpers.sharefile import ShareFile
from Helpers.sharepoint import SharePoint
from Helpers.windows import Windows
from Helpers.macos import MacOS
from Helpers.linux import Linux


class Validator:
    # A mapping of service names to their respective classes
    services = {
        "dropbox": Dropbox,
        "box": Box,
        "egnyte": Egnyte,
        "onedrive": OneDrive,
        "sharefile": ShareFile,
        "sharepoint": SharePoint,
        "windows": Windows,
        "macos": MacOS,
        "linux": Linux
    }

    def __init__(self, path: str, service_name: str = "windows"):
        self.path = path.strip().replace("\\", "/")  # Normalize the path
        self.service = self.services.get(service_name.lower(), Windows)  # Default to Windows class if not found

    def check_if_valid(self):
        service_instance = self.service(self.path)
        return service_instance.check_if_valid()

    def get_cleaned_path(self):
        service_instance = self.service(self.path)
        return service_instance.get_cleaned_path()


# Example usage
if __name__ == "__main__":
    path = "example/path/with/invalid<>characters"
    validator = Validator(path, service_name="windows")
    
    try:
        if validator.check_if_valid():
            print("Path is valid.")
        
        cleaned_path = validator.get_cleaned_path()
        print(f"Cleaned path: {cleaned_path}")

    except ValueError as e:
        print(f"Error: {e}")
