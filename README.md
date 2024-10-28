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
# the purpose of this file is just to highlight how the code can be used.
from FPV import Validator


def main():
    example_path = " /path /to./file*.txt"
    
    # Create a validator object
    validator = Validator(example_path)

    # Access the original path
    print("Original Path:", validator.original_path)

    # Get a cleaned version of your path
    cleaned_path = validator.get_cleaned_path()
    print("Cleaned Path:", cleaned_path)  # Output should be "/path/to/file.txt"

    # Check if the original path is valid
    try:
        validator.check_if_valid()
        print("Path is valid!")
    except ValueError as e:
        print(f"Validation Error: {e}")

    # Auto-clean the path upon creating the validator object
    validator_auto_clean = Validator(example_path, auto_clean=True)
    print("Automatically Cleaned Path:", validator_auto_clean.path)


if __name__ == "__main__":
    main()
```

## Notes on os_sync
- The os_sync parameter allows you to specify the operating system for additional validation checks.
- If not provided, the validator will not default to any OS. Because it is possible in a lot of cloud storage systems to only read / write files to their systems without ever syncing up the file storage to an operating system. 


## Contributing 🤝
We welcome contributions! If you'd like to help improve File Path Validator, please fork the repository and submit a pull request.

Thank you for checking out File Path Validator (FPV)! Happy coding! 🎉
