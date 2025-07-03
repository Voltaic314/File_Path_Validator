# 🎉 File Path Validator (FPV) Library Documentation

## Overview
The **File Path Validator (FPV)** library is a robust solution for validating and cleaning file paths to ensure compliance with platform-specific naming restrictions and length limits. FPV supports both operating systems and cloud storage providers, enabling seamless path validation across diverse environments. 

Many cloud storage providers strive to enforce compliance with OS-specific rules, but not all do so reliably. For instance, Google Drive syncs with Windows, requiring paths to meet Windows-specific rules, yet lacks strict enforcement on its end. FPV can bridge this gap, offering cross-platform path validation ahead of time to avoid runtime failures.

---

## Why Choose FPV?
> (From Logan - Creator of FPV):  
> "At my company, we often generate file paths for clients from a mix of disjointed data sources. This can result in messy file path strings that may fail at the storage provider or OS level. FPV ensures our paths are flagged with actionable error messages early on.  
> 
> For those who prefer automation, FPV's cleaning functionality can attempt to fix paths proactively. Whether you're debugging paths manually or streamlining cleanup, FPV has been a game-changer for us. I hope you find it equally helpful!"

---

## 🚀 Installation
Install the FPV library via pip:
```bash
pip install file-path-validator
```

---

## Supported Platforms & Providers 🌐

### 🖥️ Operating Systems
- **Windows**
- **macOS**
- **Linux**

### ☁️ Cloud Storage Providers
- **Dropbox**
- **Box**
- **Egnyte**
- **OneDrive**
- **SharePoint**
- **ShareFile**

Each class inherits from `FPV_Base`, defining unique validation and cleaning rules tailored to the platform or provider while leveraging the library's core functionality.

---

## 🛠️ Key Features and Usage Examples

### Core Arguments
FPV provides several configuration options for fine-grained control:

- **`auto_clean`**: Attempts to clean paths before validation. If issues remain unresolved after cleaning, an error is raised. Defaults to `False`.
- **`auto_validate`**: Automatically validates the path or parts upon modification. Defaults to `True`.
- **`relative`**: Determines if the path is treated as relative (`True`) or absolute (`False`). Some service classes enforce a specific behavior (e.g., macOS paths are always relative).
- **`file_added`**: Explicitly specify if the path includes a file. The library avoids assumptions about the last path part, requiring this flag for clarity.
- **`sep`**: Specifies the path separator (e.g., `"/"` for POSIX, `"\\"` for Windows). Service classes provide defaults but allow overrides.

---

### Dynamic Path Building Example

```python
from FPV import FPV_Windows

def dynamic_path_demo():
    # Instantiate the validator
    validator = FPV_Windows("C:\\", relative=False)

    # Add parts dynamically
    validator.add_part("NewFolder")
    validator.add_part("AnotherFolder")
    validator.add_part("file.txt", is_file=True)

    # Validate the dynamic path
    try:
        validator.validate()
        print("Path is valid:", validator.get_full_path())
    except ValueError as e:
        print("Validation Error:", e)

    # Review issues and actions
    print("Issues Log:", validator.get_logs()["issues"])
    print("Actions Log:", validator.get_logs()["actions"])

dynamic_path_demo()
```

---

### Logs and Action Handling
- **Issues Log**: Tracks path non-compliance (e.g., invalid characters, excessive length). Use `get_logs()["issues"]` or methods like `get_issues_for_part(index)` for targeted inspection.
- **Actions Log**: Suggests fixes (e.g., truncations, character removals). Use `get_logs()["actions"]` or `get_pending_actions_for_part(index)` for a step-by-step cleaning recipe.

Example:
```python
issues = validator.get_logs()["issues"]
actions = validator.get_logs()["actions"]

# Apply actions manually if needed
for action in actions:
    print(f"Action: {action['reason']} - Details: {action['details']}")
```

---

### Basic Example
```python
from FPV import FPV_Windows

example_path = "C:/ Broken/ **path/to/||file . txt"
validator = FPV_Windows(example_path, relative=True, sep='/')

try:
    # Validate the path
    validator.validate()
    print("Path is valid!")
except ValueError as e:
    print("Validation Error:", e)

# Clean the path
cleaned_path = validator.clean()
print("Cleaned Path:", cleaned_path)
```

---

### Recommendations for Error Handling
Wrap cleaning and validation calls in a `try-except` block to gracefully handle exceptions:
```python
try:
    cleaned_path = validator.clean()
    print("Cleaned Path:", cleaned_path)
except ValueError as e:
    print("Cleaning Error:", e)
```

---

## 🌐 REST API

FPV includes a high-performance REST API built with Quart (async Flask-compatible framework) for easy integration into web applications and microservices.

### API Features
- **Async Processing**: Handles hundreds of concurrent requests efficiently
- **Python 3.13+ Compatible**: No Pydantic dependencies
- **JSON Request/Response**: Simple REST interface
- **CORS Enabled**: Works with web applications
- **Health Monitoring**: Built-in health check endpoint

### Quick Start

#### 1. Run the API Server
```bash
# Method 1: Using the provided script
python run_api.py

# Method 2: Direct execution
python FPV/API/api.py
```

The server starts on `http://localhost:8000`

#### 2. API Endpoints

**Base URL**: `http://localhost:8000/api/v1`

##### Validate Path (`POST /isValid`)
Validates a file path according to the specified service's rules.

```bash
curl -X POST "http://localhost:8000/api/v1/isValid" \
     -H "Content-Type: application/json" \
     -d '{
       "service": "dropbox",
       "path": "/Documents/test.txt",
       "file_added": true
     }'
```

**Response**:
```json
{
  "success": true,
  "is_valid": true,
  "issues": [],
  "logs": {"actions": [], "issues": []},
  "error": null
}
```

##### Clean Path (`POST /clean`)
Cleans a file path by applying platform-specific fixes.

```bash
curl -X POST "http://localhost:8000/api/v1/clean" \
     -H "Content-Type: application/json" \
     -d '{
       "service": "windows",
       "path": "C:\\Test<Folder>\\file*.txt",
       "relative": false,
       "file_added": true
     }'
```

**Response**:
```json
{
  "success": true,
  "cleaned_path": "C:\\TestFolder\\file.txt",
  "logs": {
    "actions": [
      {
        "type": "action",
        "category": "INVALID_CHAR",
        "subtype": "MODIFY",
        "details": {
          "original": "Test<Folder>",
          "new_value": "TestFolder",
          "index": 1
        },
        "reason": "Removed invalid characters."
      }
    ],
    "issues": []
  },
  "error": null
}
```

#### 3. Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `service` | string | Yes | - | Service/platform name (windows, macos, linux, dropbox, box, egnyte, onedrive, sharepoint, sharefile) |
| `path` | string | Yes | - | File path to validate/clean |
| `relative` | boolean | No | true | Whether the path is relative (true) or absolute (false) |
| `file_added` | boolean | No | false | Whether the path includes a file |
| `sep` | string | No | platform default | Path separator (e.g., "/", "\\") |

#### 4. Python Client Example

```python
import requests

# Validate a path
response = requests.post("http://localhost:8000/api/v1/isValid", json={
    "service": "dropbox",
    "path": "/Documents/test.txt",
    "file_added": True
})
result = response.json()
print(f"Path is valid: {result['is_valid']}")

# Clean a path
response = requests.post("http://localhost:8000/api/v1/clean", json={
    "service": "windows",
    "path": "C:\\Test<Folder>\\file*.txt",
    "relative": False,
    "file_added": True
})
result = response.json()
print(f"Cleaned path: {result['cleaned_path']}")
```

#### 5. Performance

The API is optimized for high-throughput scenarios:
- **Concurrent Requests**: Handles hundreds of requests per second
- **Async Processing**: Non-blocking I/O for better performance
- **Memory Efficient**: Minimal overhead for in-memory path processing
- **Localhost Optimized**: Fast response times for local deployments

---

## ⚙️ Key Methods
- **`validate()`**: Validates the entire path. Raises `ValueError` if issues are found unless `raise_error=False` is explicitly set.
- **`clean()`**: Cleans the path to meet compliance rules, applying fixes from the action log. Raises errors for unresolved issues if `raise_error=True`.

---

## Limitations and Future Plans
- **Missing Features**: SharePoint site URLs and encoded paths are not yet supported.
- **Network Drives**: Windows network drive root validation is not supported (though non-root parts are fully validated).
- **User-Defined Order**: Cleaning/validation order cannot yet be customized but can be manually controlled.

---

## 🤝 Contributing Guidelines
We welcome contributions! Please adhere to the following:
- **Testing**: Include unit tests for all new features or bug fixes.
- **Standards**: Ensure code follows PEP-8 standards or run a linter before submission.
- **Pull Requests**: Clearly describe your changes and their purpose.

Thank you for helping improve FPV! 🎉