Methodology for File Path Validation

Overview

The File Path Validator is designed to ensure that file paths conform to the restrictions and requirements imposed by different storage services and operating systems. Our methodology focuses on providing a flexible and extensible system that can adapt to various scenarios, allowing users to validate paths effectively based on their specific needs.


Core Components
Validator Class

The central component of our validation system is the Validator class. This class is responsible for:

    Normalizing the input file path.
    Instantiating the appropriate storage service class based on user input.
    Executing the necessary checks to validate the path against both the storage service and the specified operating system constraints.

Usage

When creating an instance of the Validator, users can specify:

Path: The file path to be validated.
Service Name: The storage service for which the validation is performed (e.g., box, dropbox, onedrive).
OS Sync: An optional argument that indicates whether the validation should take into account the operating system's restrictions (e.g., windows, macos, linux). If this argument is provided, the validator will perform additional checks specific to the operating system.

OS Classes

Each OS class (e.g., Windows, MacOS, Linux) inherits from the base service class and implements OS-specific restrictions and checks. These classes are structured to allow for:

    Path Length Limitations: Each OS has its own maximum path length, and our system respects these limitations.
    Reserved Names and Characters: Each OS class checks for reserved names and invalid characters that may lead to errors when interacting with the file system.

Methodology for Using os_sync

    When to Use os_sync: The os_sync argument is useful when files are intended to be accessed natively within the specified operating system. By specifying this argument, users ensure that all relevant OS restrictions are checked, helping to prevent issues when the file paths are used in their respective file explorers.

    Default Behavior: If not provided, the validator will not default to any OS. Because it is possible in a lot of cloud storage systems to only read / write files to their systems without ever syncing up the file storage to an operating system.


Conclusion

The design of the File Path Validator emphasizes flexibility, allowing it to be used across various platforms and storage services. By modularizing the validation logic into service and OS-specific classes, we maintain a clean and efficient codebase while providing thorough validation checks to prevent file system errors.
