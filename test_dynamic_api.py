#!/usr/bin/env python3
"""
Test script for FPV Dynamic Path Building API
Demonstrates how ByteWave or other applications can use the API for incremental path building
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_dynamic_path_building():
    """Test the dynamic path building endpoints"""
    
    print("🚀 Testing FPV Dynamic Path Building API")
    print("=" * 50)
    
    # Test 1: Add parts incrementally (like ByteWave building a path)
    print("\n1️⃣ Testing incremental path building (add parts):")
    print("-" * 40)
    
    # Start with root path
    base_path = "C:\\"
    current_errors = []
    
    # Add parts one by one (simulating user input)
    parts_to_add = ["Users", "golde", "Documents", "Project Files"]
    
    for i, part in enumerate(parts_to_add):
        print(f"Adding part {i+1}: '{part}'")
        
        response = requests.post(f"{BASE_URL}/path/add", json={
            "service": "windows",
            "base_path": base_path,
            "parts": [part],
            "errors": current_errors,
            "validate": True,
            "relative": False,
            "file_added": False
        })
        
        if response.status_code == 200:
            result = response.json()
            base_path = result["updated_path"]
            current_errors = result["all_errors"]
            
            print(f"  ✅ Path: {base_path}")
            if result["new_errors"]:
                print(f"  ⚠️  New errors: {len(result['new_errors'])}")
            else:
                print(f"  ✅ No new errors")
        else:
            print(f"  ❌ Error: {response.text}")
            break
    
    print(f"\nFinal path: {base_path}")
    print(f"Total errors: {len(current_errors)}")
    
    # Test 2: Add a file
    print("\n2️⃣ Adding a file to the path:")
    print("-" * 40)
    
    response = requests.post(f"{BASE_URL}/path/add", json={
        "service": "windows",
        "base_path": base_path,
        "parts": ["document.txt"],
        "errors": current_errors,
        "validate": True,
        "relative": False,
        "file_added": True
    })
    
    if response.status_code == 200:
        result = response.json()
        final_path = result["updated_path"]
        final_errors = result["all_errors"]
        
        print(f"✅ Final path with file: {final_path}")
        print(f"Total errors: {len(final_errors)}")
        
        if final_errors:
            print("Errors found:")
            for error in final_errors:
                print(f"  - {error}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 3: Remove a part
    print("\n3️⃣ Removing a path part:")
    print("-" * 40)
    
    response = requests.post(f"{BASE_URL}/path/remove", json={
        "service": "windows",
        "base_path": final_path,
        "part_index": 2,  # Remove "golde"
        "errors": final_errors,
        "relative": False,
        "file_added": True
    })
    
    if response.status_code == 200:
        result = response.json()
        updated_path = result["updated_path"]
        remaining_errors = result["remaining_errors"]
        
        print(f"✅ Path after removal: {updated_path}")
        print(f"Remaining errors: {len(remaining_errors)}")
        print(f"Removed part: {result['removed_part']}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test 4: Build path incrementally with full tracking
    print("\n4️⃣ Building path with full step tracking:")
    print("-" * 40)
    
    response = requests.post(f"{BASE_URL}/path/build", json={
        "service": "dropbox",
        "root_path": "/",
        "path_parts": ["Documents", "Work", "Reports", "Q4_Report.pdf"],
        "relative": True,
        "file_added": True
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Final path: {result['final_path']}")
        print(f"Total errors: {len(result['all_errors'])}")
        
        print("\nStep-by-step validation:")
        for step in result["step_errors"]:
            status = "✅" if not step["issues"] else "⚠️"
            print(f"  {status} Step {step['step']}: '{step['part']}' - {len(step['issues'])} issues")
    else:
        print(f"❌ Error: {response.text}")

def test_concurrent_requests():
    """Test concurrent requests to demonstrate async performance"""
    
    print("\n🔄 Testing concurrent requests:")
    print("-" * 40)
    
    import concurrent.futures
    import threading
    
    def make_request(thread_id):
        """Make a single request"""
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/path/add", json={
            "service": "windows",
            "base_path": "C:\\",
            "parts": [f"folder_{thread_id}"],
            "errors": [],
            "validate": True,
            "relative": False,
            "file_added": False
        })
        
        end_time = time.time()
        return {
            "thread_id": thread_id,
            "status_code": response.status_code,
            "response_time": end_time - start_time,
            "success": response.status_code == 200
        }
    
    # Test with 10 concurrent requests
    num_requests = 10
    print(f"Making {num_requests} concurrent requests...")
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    total_time = end_time - start_time
    
    successful = sum(1 for r in results if r["success"])
    avg_response_time = sum(r["response_time"] for r in results) / len(results)
    
    print(f"✅ Completed {num_requests} requests in {total_time:.2f}s")
    print(f"✅ Successful: {successful}/{num_requests}")
    print(f"✅ Average response time: {avg_response_time:.3f}s")
    print(f"✅ Requests per second: {num_requests/total_time:.1f}")

def test_error_handling():
    """Test error handling scenarios"""
    
    print("\n🚨 Testing error handling:")
    print("-" * 40)
    
    # Test invalid service
    print("Testing invalid service...")
    response = requests.post(f"{BASE_URL}/path/add", json={
        "service": "invalid_service",
        "base_path": "C:\\",
        "parts": ["test"],
        "errors": []
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test missing required fields
    print("\nTesting missing required fields...")
    response = requests.post(f"{BASE_URL}/path/add", json={
        "service": "windows",
        "base_path": "C:\\"
        # Missing parts and errors
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    try:
        # Test the main functionality
        test_dynamic_path_building()
        
        # Test concurrent performance
        test_concurrent_requests()
        
        # Test error handling
        test_error_handling()
        
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on http://localhost:8000")
        print("Run: python run_api.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 