# 🌟 Developer Guide to File Path Validator (FPV)

## Overview
The **File Path Validator (FPV)** library is designed with a modular and extensible architecture to validate and clean file paths across various platforms and services. This guide provides an understanding of how the library is structured, how its components interact, and how to contribute by adding new features or improving existing functionality.

---

## 📂 Project Structure
The codebase is organized into three main directories:

```
FPV/
├── Helpers/          # Core classes and logic
│   ├── _base.py       # Base class for validation and cleaning
│   ├── _path.py       # Path helper class for managing path parts, logs, and actions
│   ├── os_classes.py  # Classes for Windows, macOS, Linux validation
│   ├── <service_classes>.py  # Cloud service-specific classes (e.g., FPV_Dropbox, FPV_OneDrive)
├── Tests/            # Unit tests for the core and service-specific functionality
│   ├── test_path.py   # Tests for _path.py
│   ├── test_base.py   # Tests for the base class
│   ├── test_<service>.py  # Tests for service-specific methods
```

---

## 🔧 Key Components

### 1. _base.py (Base Class)
The **`FPV_Base`** class defines the foundation for all service-specific classes. It provides:
- **Core Methods**:
  - `validate()`: Validates the path by checking for platform-specific or service-specific restrictions.
  - `clean()`: Attempts to clean the path, removing invalid characters, truncating lengths, etc.
- **Dynamic Behavior**:
  - Validation and cleaning are controlled by `auto_validate` and `auto_clean` arguments.
  - Explicitly distinguishes between files and folders to avoid incorrect assumptions about path parts.
- **Processing Pipeline**:
  - Calls `process_<type>` methods (e.g., `process_invalid_characters`) to validate or clean individual path parts.
  - Uses `processing_methods()` to map validation/cleaning functions to path parts (e.g., root, folder, file).

#### Extending `FPV_Base`
To add custom functionality:
1. Add a new `process_<type>` method for the desired behavior.
2. Include the new method in the `processing_methods()` dictionary of the subclass.
3. Write corresponding tests in the `Tests/` directory.

---

### 2. _path.py (Path Helper)
The **Path Helper** manages the internal representation of a file path as a list of parts. It:
- **Path Management**:
  - Splits a path into parts (e.g., root, folders, file).
  - Supports dynamic modification via `add_part()` and `remove_part()`.
- **Action/Issue Logs**:
  - Logs validation issues and cleaning actions to provide an audit trail.
  - Enables users to replay actions for generating a cleaned path.
- **Utilities**:
  - Provides helper methods like `get_issues_for_part()` and `get_pending_actions_for_part()` for granular control.

#### Key Methods
- `add_issue(issue: dict)`: Adds a validation issue to the logs.
- `add_action(action: dict, priority: int)`: Adds a cleaning action with a priority to ensure correct execution order.
- `apply_actions()`: Applies queued actions to modify the path dynamically.

---

### 3. Service Classes
Each platform or service (e.g., Windows, Dropbox) has a dedicated subclass inheriting from `FPV_Base`. Service classes:
- Override `invalid_characters`, `restricted_names`, and other constraints.
- Define platform-specific or service-specific validation and cleaning rules via `processing_methods()`.

#### Example: Dropbox Class
```python
class FPV_Dropbox(FPV_Base):
    invalid_characters = '<>:"|?*.'
    max_length = 260

    def process_invalid_characters(self, part, action):
        if part.get("is_file", False):
            self.invalid_characters = self.invalid_characters.replace(".", "")
        cleaned_part = super().process_invalid_characters(part, action)
        self.invalid_characters = '<>:"|?*.'
        return cleaned_part

    def processing_methods(self):
        return {
            "folder": [
                lambda part, action: self.process_invalid_characters(part, action),
                # Other processing methods...
            ],
            "file": [
                lambda part, action: self.process_invalid_characters(part, action),
                # Other processing methods...
            ],
        }
```

---

## 🛠️ Adding a New Subclass
1. Create a new file under `Helpers/` for the new platform or service.
2. Inherit from `FPV_Base`.
3. Override any platform-specific constants or add unique processing methods.
4. Write tests in `Tests/` to cover the new functionality.

Example:
```python
class FPV_NewService(FPV_Base):
    invalid_characters = '<>:"|?*'
    max_length = 300

    def processing_methods(self):
        return {
            "root": [
                lambda part, action: self.process_invalid_characters(part, action),
            ],
            "folder": [
                lambda part, action: self.process_invalid_characters(part, action),
            ],
            "file": [
                lambda part, action: self.process_invalid_characters(part, action),
            ],
        }
```

---

## 🧪 Testing Guidelines
- Place tests in `Tests/` with the naming convention `test_<module>.py`.
- Use `pytest` for consistent test structure.
- Focus tests on:
  - Custom `process_<type>` methods.
  - Integration with the `FPV_Base` class.
  - Edge cases for platform-specific rules.

---

## 📢 Contribution Guidelines
1. **Fork and Clone**: Fork the repo and create a feature branch.
2. **Follow PEP-8**: Ensure all code follows Python's PEP-8 guidelines.
3. **Write Tests**: All new features must include tests.
4. **Document Changes**: Update the README or other relevant documentation.

---

Thank you for contributing to FPV! 🎉
