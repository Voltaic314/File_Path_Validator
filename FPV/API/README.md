# File Path Validator API

A FastAPI-based REST API for the File Path Validator (FPV) library that provides endpoints for validating and cleaning file paths across different platforms and cloud storage providers.

## Features

- **Path Validation**: Check if file paths comply with platform-specific rules
- **Path Cleaning**: Automatically fix common path issues
- **Multi-Platform Support**: Windows, macOS, Linux, and major cloud storage providers
- **RESTful API**: Easy-to-use HTTP endpoints with JSON request/response
- **Auto-generated Documentation**: Interactive API docs with Swagger UI

## Quick Start

### 1. Install Dependencies

```bash
pip install -r FPV/requirements.txt
```

### 2. Run the API Server

```bash
python run_api.py
```

The server will start on `http://localhost:8000`

### 3. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### 1. Validate Path (`POST /isValid`)

Validates a file path according to the specified service's rules.

**Request Body:**
```json
{
    "service": "dropbox",
    "path": "/Documents/test.txt",
    "relative": true,
    "file_added": true,
    "sep": "/"
}
```

**Response:**
```json
{
    "success": true,
    "is_valid": true,
    "issues": [],
    "logs": {
        "actions": [],
        "issues": []
    },
    "error": null
}
```

### 2. Clean Path (`POST /clean`)

Cleans a file path by applying platform-specific fixes.

**Request Body:**
```json
{
    "service": "windows",
    "path": "C:\\Test<Folder>\\file*.txt",
    "relative": false,
    "file_added": true
}
```

**Response:**
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

## Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `service` | string | Yes | - | Service/platform name (windows, macos, linux, dropbox, box, egnyte, onedrive, sharepoint, sharefile) |
| `path` | string | Yes | - | File path to validate/clean |
| `relative` | boolean | No | true | Whether the path is relative (true) or absolute (false) |
| `file_added` | boolean | No | false | Whether the path includes a file |
| `sep` | string | No | platform default | Path separator (e.g., "/", "\\") |

## Supported Services

### Operating Systems
- `windows` - Windows file system rules
- `macos` - macOS file system rules  
- `linux` - Linux file system rules

### Cloud Storage Providers
- `dropbox` - Dropbox storage rules
- `box` - Box storage rules
- `egnyte` - Egnyte storage rules
- `onedrive` - OneDrive storage rules
- `sharepoint` - SharePoint storage rules
- `sharefile` - ShareFile storage rules

## Testing the API

Run the test script to see examples:

```bash
python test_api.py
```

Or use curl:

```bash
# Validate a path
curl -X POST "http://localhost:8000/api/v1/isValid" \
     -H "Content-Type: application/json" \
     -d '{"service": "dropbox", "path": "/test/file.txt", "file_added": true}'

# Clean a path
curl -X POST "http://localhost:8000/api/v1/clean" \
     -H "Content-Type: application/json" \
     -d '{"service": "windows", "path": "C:\\test<file>.txt", "relative": false, "file_added": true}'
```

## Error Handling

The API returns structured error responses:

```json
{
    "success": false,
    "is_valid": false,
    "issues": [],
    "logs": {},
    "error": "Unsupported service: invalid_service. Supported services: ['windows', 'macos', 'linux', 'dropbox', 'box', 'egnyte', 'onedrive', 'sharepoint', 'sharefile']"
}
```

## Development

### Running in Development Mode

The server runs with auto-reload enabled by default. Any changes to the code will automatically restart the server.

### Project Structure

```
FPV/API/
├── api.py                 # Main FastAPI application
├── routes/
│   └── path/
│       ├── clean.py       # Clean endpoint
│       └── isValid.py     # Validate endpoint
└── README.md             # This file
```

### Adding New Endpoints

1. Create a new router file in `routes/`
2. Define request/response models using Pydantic
3. Add the router to `api.py`
4. Update the main `__init__.py` if needed

## License

This API is part of the File Path Validator library and follows the same license terms. 