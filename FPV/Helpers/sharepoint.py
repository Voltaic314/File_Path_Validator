import re
from FPV.Helpers._base import FPV_Base
from urllib.parse import quote, unquote

class FPV_SharePoint(FPV_Base):
    # Invalid characters specific to SharePoint, adding "#" to the base invalid characters
    invalid_characters = FPV_Base.invalid_characters + "#"

    def __init__(self, path: str, auto_clean=False, relative=True):
        super().__init__(path, auto_clean=auto_clean, relative=relative)
        self.auto_clean = auto_clean
        self.relative = relative
        self.original_path = path
        self.is_site_url = "https://" in self.path or "http://" in self.path
        if self.is_site_url:
            # for example, if it's https://example.sharepoint.com then the site domain is "example"
            self.site_domain = self.path.split("//")[1].split(".sharepoint")[0]
            # the file path comes after the "sites/" portion of the URL
            self.path = unquote("/".join(self.path.split("sites/")[1:])) # this is a really handy way to get just the file path of the specific site path url. :) 

        # SharePoint-specific restricted names, prefixes, and root folder
        self.max_length = 400
        self.restricted_names = {
            ".lock", "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", 
            "COM6", "COM7", "COM8", "COM9", "LPT1", 
            "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", 
            "LPT7", "LPT8", "LPT9", "_vti_", "desktop.ini"
        }
        self.restricted_prefix = "~$"
        self.restricted_root_folder = "forms"

        self.corresponding_validate_and_clean_methods.update(
            {"restricted_prefix": {"validate": "validate_restricted_prefix", "clean": "remove_restricted_prefix"},
             "restricted_root_folder": {"validate": "validate_restricted_root_folder", "clean": "remove_restricted_root_folder"},
             "site_domain": {"validate": "validate_site_domain", "clean": "clean_site_domain"}
            }
        )
        
        if self.auto_clean:
            self.path = self.clean()

    def validate_site_domain(self):
        """Validate the site domain part of the SharePoint URL."""
        if not re.match(r"^[a-zA-Z0-9-]+$", self.site_domain):
            raise ValueError(f'Invalid characters found in site domain: "{self.site_domain}"')
        self.validate_if_whitespace_around_parts(path=self.site_domain)
        if "/" in self.site_domain:
            raise ValueError(f'Invalid character "/" found in site domain: "{self.site_domain}"')

        if self.site_domain.lower() in self.restricted_names:
            raise ValueError(f'Restricted name "{self.site_domain}" found in site domain')
        
        if self.site_domain.startswith(self.restricted_prefix):
            raise ValueError(f'Restricted prefix "{self.restricted_prefix}" found in site domain: "{self.site_domain}"')
        
    def clean_site_domain(self):
        """Clean and return the site domain part of the SharePoint URL."""
        cleaned_site_domain = self.clean_and_validate_path("restricted_names", path=self.site_domain)
        cleaned_site_domain = self.clean_and_validate_path("restricted_prefix", path=cleaned_site_domain)
        cleaned_site_domain = cleaned_site_domain.strip().rstrip(".")
        return cleaned_site_domain


    def validate(self):
        """Validate the full path for SharePoint, including SharePoint-specific validations."""
        self.validate_path_length(path=self.original_path) # specifically we need to validate that the whole sharepoint url is less than the max char length.
        # btw the 400 char limit applies to the *quoted* url. So a single space counts as 3 characters lol. Kind of silly in my opinion. 
        self.validate_invalid_characters()
        self.validate_restricted_names()
        self.validate_if_part_ends_with_period()
        self.validate_if_whitespace_around_parts()
        if self.site_domain:
            self.validate_site_domain()

        # Apply SharePoint-specific checks on each part
        for part in self.path_parts:
            self.validate_restricted_prefix(part)
            self.validate_restricted_root_folder(part)
        
        self.validate_empty_parts()

    def clean(self, raise_error=True, path=''):
        """Clean and return a SharePoint-compliant path; validate if raise_error is True."""
        cleaned_path = self.path if not path else path
        cleaned_path = self.clean_and_validate_path("path_length", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("invalid_characters", path=cleaned_path)
        cleaned_path = self.clean_and_validate_path("restricted_names", path=cleaned_path)

        # Remove restricted prefixes and handle root folder restrictions
        cleaned_path_parts = []
        for index, part in enumerate(cleaned_path.split("/")):
            part = self.remove_restricted_prefix(part)
            if index == 0:
                part = self.remove_restricted_root_folder(part)
            part = part.strip().rstrip(".")
            if part:
                cleaned_path_parts.append(part)
        
        cleaned_path = "/".join(cleaned_path_parts).strip("/")
        cleaned_path = f"/{cleaned_path}" if not cleaned_path.startswith("/") else cleaned_path

        # Revalidate if needed
        if raise_error:
            cleaned_path_instance = FPV_SharePoint(cleaned_path, auto_clean=False, relative=self.relative)
            cleaned_path_instance.validate()

        return cleaned_path

    # SharePoint-specific helper methods
    def validate_restricted_prefix(self, part):
        """Validate that a part of the path does not start with the restricted prefix."""
        if part.startswith(self.restricted_prefix):
            raise ValueError(f'Restricted prefix "{self.restricted_prefix}" found in path part: "{part}"')

    def validate_restricted_root_folder(self, part):
        """Validate that the first part of the path is not the restricted root folder."""
        if part.lower() == self.restricted_root_folder and self.path_parts.index(part) == 0:
            raise ValueError(f'Restricted root folder "{self.restricted_root_folder}" found at path root: "{part}"')

    def remove_restricted_prefix(self, part):
        """Remove the restricted prefix from a path part if present."""
        return part[len(self.restricted_prefix):] if part.startswith(self.restricted_prefix) else part

    def remove_restricted_root_folder(self, part):
        """Remove the restricted root folder name if it is the first part of the path."""
        return "" if part.lower() == self.restricted_root_folder else part
