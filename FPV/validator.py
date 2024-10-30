# Import storage service classes
from FPV.Helpers.box import Box
from FPV.Helpers.dropbox import Dropbox
from FPV.Helpers.egnyte import Egnyte
from FPV.Helpers.onedrive import OneDrive
from FPV.Helpers.sharefile import ShareFile
from FPV.Helpers.sharepoint import SharePoint

# import Operating System classes
from FPV.Helpers._os_classes import Windows, MacOS, Linux


class Validator:
    # A mapping of service names to their respective classes
    services = {
        "dropbox": Dropbox,
        "box": Box,
        "egnyte": Egnyte,
        "onedrive": OneDrive,
        "sharefile": ShareFile,
        "sharepoint": SharePoint,
    }

    # A mapping of OS names to their respective classes
    os_services = {
        "windows": Windows,
        "macos": MacOS,
        "linux": Linux
    }

    def __init__(self, path: str, service_name: str = "windows", os_sync: str = None, **kwargs):
        self.original_path = path  # Store the original unmodified path
        self.path = path.replace("\\", "/")  # Normalize the path
        self.path = f"/{self.path}" if not self.path.startswith("/") else self.path  # Ensure path starts with a forward slash
        self.os_sync = os_sync  # Store the OS sync option
        self.auto_clean = kwargs.get("auto_clean", False)  # Store the auto_clean flag

        # Determine if we're using a storage service or an OS service
        if service_name.lower() in self.services:
            self.service = self.services[service_name.lower()](self.path, **kwargs)  # Instantiate the service provider
        elif service_name.lower() in self.os_services:
            self.service = self.os_services[service_name.lower()](self.path, **kwargs)  # Instantiate the OS provider
        else:
            # Default to Windows service if not found
            self.service = Windows(self.path, **kwargs)

        # If os_sync is provided and not an OS service, instantiate the appropriate OS class
        if os_sync and os_sync.lower() in self.os_services and service_name.lower() not in self.os_services:
            os_service_class = self.os_services[os_sync.lower()]
            self.os_service = os_service_class(self.path, **kwargs)  # Instantiate the OS class
        else:
            self.os_service = None  # No OS-specific checks

        if self.auto_clean:
            self.path = self.clean()  # Clean the path if auto_clean is set

    def validate(self):
        # First, validate the storage service
        self.service.validate()
        
        # If os_sync is provided, validate the OS-specific checks
        if self.os_service:
            self.os_service.validate()

    def clean(self):
        cleaned_path = self.service.clean()  # Get cleaned path from the service
        # If os_sync is provided, we can optionally return the cleaned path from the OS service as well if needed
        if self.os_service:
            cleaned_path = self.os_service.clean()  # Adjust based on OS checks if necessary
        return cleaned_path
