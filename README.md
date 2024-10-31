
# 🎉 File Path Validator (FPV) Library Documentation

## Overview
The **File Path Validator (FPV)** library validates and cleans file paths to ensure they meet platform-specific naming restrictions and length limits. It’s compatible with multiple operating systems and cloud storage providers, providing automated path validation across various services. Many cloud storage providers try to make sure that their platform is compliant with operating system specific rules as well. So one could also use this library to ensure paths are cross-platform compliant ahead of time too if the storage provider is not doing this. For example, Google Drive does not have many restrictions, but in order to sync with windows they need to ensure paths meet windows'path rules. So this library can be used to help with that task.


## Why even do this at all?
(From Logan - The creator of this library): "Often times at my company we have to generate file paths for clients using various disjointed sources of information and bits of data. This can lead to messy file path strings. We do what we can to clean it up, but this library gives us reassurance that our files are being flagged with more helpful error messages before it gets to the point of failing at the storage provider / OS. -- It's also worth noting if you want to be lazy and have this library attempt to clean your paths for you, it can do that as well using the clean method of the given class you are using. I hope you will find this library as helpful and useful as I do."

## 🚀 Installation
To install the FPV library, run the following:
```bash
pip install file-path-validator
```

## Supported Platforms & Providers 🌐
FPV provides support for the following:

### 🖥️ Operating Systems
- **Windows**
- **macOS**
- **Linux**

### ☁️ Cloud Storage Providers
- **Dropbox**
- **Egnyte**
- **OneDrive**
- **SharePoint**
- **ShareFile**

Each class inherits from `FPV_Base` and introduces platform-specific restrictions. Subclasses define their unique validation and cleaning rules while leveraging the base class’s core validation and cleaning functionality.

## Usage Example 🛠️
The following example demonstrates basic usage with `FPV_Windows`:

```python
from FPV import FPV_Windows

def main():
    example_path = "C:/ Broken/ **path/to||file . txt"
    
    # Create a validator object
    FPVW = FPV_Windows(example_path, relative=True)

    # Access the original path
    print("Original Path:", FPVW.original_path)

    # Get a cleaned version of your path
    cleaned_path = FPVW.clean()
    print("Cleaned Path:", cleaned_path)  # Output should be "/path/to/file.txt"

    # Check if the original path is valid
    try:
        FPVW.validate()
        print("Path is valid!")
    except ValueError as e:
        print(f"Validation Error: {e}")

    # Auto-clean the path upon creating the validator object
    validator_auto_clean = FPV_Windows(example_path, auto_clean=True, relative=True)
    print("Automatically Cleaned Path:", validator_auto_clean.path)

    ## instantiate more objects... As many as you need to see the validation for each. :)

if __name__ == "__main__":
    main()
```

## ⚙️ Key Methods
- **`validate()`**: Runs all validation checks for the platform or service, raising `ValueError` if issues are found.
- **`clean(raise_error=True)`**: Cleans the path to be compliant with the platform’s rules. If `raise_error=True`, it raises an exception for any uncleanable issues. 

## 🤝 Contributing Guidelines
Contributions are welcome! Please follow these guidelines:

- **Add Tests**: Ensure new features or bug fixes come with corresponding tests.
- **Run All Tests**: Before submitting a pull request, confirm that all tests (existing and new) pass.
- **Code Formatting**: Format code to PEP-8 standards or, at minimum, run a linter before submission.
- **PR Description**: Briefly explain your contribution's purpose and details on how it improves, fixes, or adds to the library.

Thank you for helping improve FPV! 🎉
