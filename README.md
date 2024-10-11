# File Path Validator (FPV) 🚀

Welcome to **File Path Validator (FPV)**! This Python package provides a robust solution for validating file paths across different operating systems and cloud storage providers, ensuring that your paths are safe and compliant with the respective file system rules. 🖥️✨

## Features 🌟

- **Cross-Platform Support**: Validates file paths for Windows, macOS, and Linux.
- **User-Friendly Error Messages**: Easy-to-understand error messages for non-tech-savvy users.
- **Customizable Validation**: Supports various file name restrictions and length limitations.

## Supported Platforms 🖥️

### Operating Systems
- Windows
- macOS
- Linux (Debian/Ubuntu)

### Cloud Storage Providers
- Box
- Dropbox
- Egnyte
- OneDrive
- SharePoint
- ShareFile

## Installation 📦

To install **File Path Validator**, clone the repository and install it using pip:

```bash
pip install file-path-validator
```

## Usage 📖

```python
from FPV import Validator  # Import the Validator class from the FPV package

path = "example/path/with/invalid<>characters"
validator = Validator(path, service_name="windows")  # Specify the service name and path

try:
    validator.check_if_valid()  # Validate the file path
    cleaned_path = validator.get_cleaned_path()  # Get the cleaned path
    print("Path is valid!")
    print(f"Cleaned path: {cleaned_path}")
except ValueError as e:
    print(f"Error: {e}")
```

## Notes on os_sync
- The os_sync parameter allows you to specify the operating system for additional validation checks.
- If not provided, the validator defaults to Windows checks, assuming the user primarily works in that environment.


## Contributing 🤝
We welcome contributions! If you'd like to help improve File Path Validator, please fork the repository and submit a pull request.

Thank you for checking out File Path Validator (FPV)! Happy coding! 🎉
