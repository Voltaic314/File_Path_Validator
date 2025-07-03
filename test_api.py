#!/usr/bin/env python3
"""
Test script to demonstrate the File Path Validator API endpoints.
Make sure the API server is running before executing this script.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_validate_endpoint():
    """Test the /isValid endpoint."""
    print("=== Testing /isValid endpoint ===")
    
    # Test case 1: Valid Dropbox path
    payload = {
        "service": "dropbox",
        "path": "/Documents/test.txt",
        "file_added": True
    }
    
    response = requests.post(f"{BASE_URL}/isValid", json=payload)
    print(f"Valid Dropbox path test:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test case 2: Invalid Windows path with special characters
    payload = {
        "service": "windows",
        "path": "C:\\Test<Folder>\\file*.txt",
        "relative": False,
        "file_added": True
    }
    
    response = requests.post(f"{BASE_URL}/isValid", json=payload)
    print(f"Invalid Windows path test:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_clean_endpoint():
    """Test the /clean endpoint."""
    print("=== Testing /clean endpoint ===")
    
    # Test case 1: Clean a messy Dropbox path
    payload = {
        "service": "dropbox",
        "path": "/Documents/  messy**folder  /file.txt",
        "file_added": True
    }
    
    response = requests.post(f"{BASE_URL}/clean", json=payload)
    print(f"Clean Dropbox path test:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test case 2: Clean a Windows path with invalid characters
    payload = {
        "service": "windows",
        "path": "C:\\Test<Folder>\\file*.txt",
        "relative": False,
        "file_added": True
    }
    
    response = requests.post(f"{BASE_URL}/clean", json=payload)
    print(f"Clean Windows path test:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_root_endpoint():
    """Test the root endpoint."""
    print("=== Testing root endpoint ===")
    
    response = requests.get("http://localhost:8000/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    try:
        # Test root endpoint first
        test_root_endpoint()
        
        # Test validation endpoint
        test_validate_endpoint()
        
        # Test clean endpoint
        test_clean_endpoint()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running by executing: python run_api.py")
    except Exception as e:
        print(f"Error: {e}") 