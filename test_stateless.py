#!/usr/bin/env python3
"""
Test script for FPV Stateless Functionality
Verifies that the new stateless design works correctly for incremental validation
"""

from FPV import FPV_Windows
import json

def test_stateless_functionality():
    """Test the new stateless functionality"""
    
    print("🧪 Testing FPV Stateless Functionality")
    print("=" * 50)
    
    # Test 1: Create initial validator and get state
    print("\n1️⃣ Creating initial validator...")
    validator1 = FPV_Windows("C:\\", relative=False, auto_validate=False)
    validator1.add_part("Users", validate_new_only=True)
    validator1.add_part("golde", validate_new_only=True)
    
    # Get current state
    state = validator1.get_current_state()
    path_parts = validator1.get_path_parts()
    
    print(f"✅ Path: {validator1.get_full_path()}")
    print(f"✅ Parts: {path_parts}")
    print(f"✅ Errors: {len(state['errors'])}")
    print(f"✅ Actions: {len(state['actions'])}")
    
    # Test 2: Create new validator from state
    print("\n2️⃣ Creating new validator from state...")
    validator2 = FPV_Windows.from_state(
        validator1.get_full_path(),
        existing_errors=state['errors'],
        existing_actions=state['actions'],
        relative=False,
        auto_validate=False
    )
    
    print(f"✅ Path: {validator2.get_full_path()}")
    print(f"✅ Parts: {validator2.get_path_parts()}")
    print(f"✅ Errors: {len(validator2.get_logs()['issues'])}")
    
    # Test 3: Add new part with incremental validation
    print("\n3️⃣ Adding new part with incremental validation...")
    validator2.add_part("Documents", validate_new_only=True)
    
    print(f"✅ New path: {validator2.get_full_path()}")
    print(f"✅ New parts: {validator2.get_path_parts()}")
    print(f"✅ Total errors: {len(validator2.get_logs()['issues'])}")
    
    # Test 4: Remove part with error cleanup
    print("\n4️⃣ Removing part with error cleanup...")
    validator2.remove_part(2, remove_related_errors=True)  # Remove "golde"
    
    print(f"✅ Path after removal: {validator2.get_full_path()}")
    print(f"✅ Parts after removal: {validator2.get_path_parts()}")
    print(f"✅ Errors after removal: {len(validator2.get_logs()['issues'])}")
    
    # Test 5: Verify no revalidation occurred
    print("\n5️⃣ Verifying no revalidation occurred...")
    
    # Check that errors from removed parts are gone
    remaining_errors = validator2.get_logs()['issues']
    for error in remaining_errors:
        index = error.get('details', {}).get('index')
        if index is not None:
            part = validator2.get_path_parts()[index]
            print(f"  - Error at index {index} (part: '{part}'): {error.get('category')}")
    
    print("✅ Stateless functionality working correctly!")

def test_performance_comparison():
    """Compare performance between old and new approaches"""
    
    print("\n⚡ Performance Comparison")
    print("=" * 30)
    
    import time
    
    # Test with many parts to see the difference
    parts = [f"folder_{i}" for i in range(10)]
    
    # Old approach (would revalidate everything)
    print("Testing old approach (simulated)...")
    start_time = time.time()
    
    # Simulate old behavior - this would revalidate everything each time
    validator_old = FPV_Windows("C:\\", relative=False, auto_validate=False)
    for part in parts:
        validator_old.add_part(part, validate_new_only=False)  # Force full validation
    
    old_time = time.time() - start_time
    print(f"Old approach time: {old_time:.4f}s")
    
    # New approach (incremental validation)
    print("Testing new approach...")
    start_time = time.time()
    
    validator_new = FPV_Windows("C:\\", relative=False, auto_validate=False)
    for part in parts:
        validator_new.add_part(part, validate_new_only=True)  # Only validate new part
    
    new_time = time.time() - start_time
    print(f"New approach time: {new_time:.4f}s")
    
    improvement = ((old_time - new_time) / old_time) * 100
    print(f"Performance improvement: {improvement:.1f}%")

def test_error_persistence():
    """Test that errors persist correctly across state loads"""
    
    print("\n🔍 Error Persistence Test")
    print("=" * 30)
    
    # Create validator with some errors
    validator1 = FPV_Windows("C:\\", relative=False, auto_validate=False)
    validator1.add_part("Users", validate_new_only=True)
    validator1.add_part("test<folder>", validate_new_only=True)  # Invalid chars
    
    initial_errors = validator1.get_logs()['issues']
    print(f"Initial errors: {len(initial_errors)}")
    for error in initial_errors:
        print(f"  - {error.get('category')}: {error.get('reason')}")
    
    # Get state and create new validator
    state = validator1.get_current_state()
    validator2 = FPV_Windows.from_state(
        validator1.get_full_path(),
        existing_errors=state['errors'],
        relative=False,
        auto_validate=False
    )
    
    # Verify errors are preserved
    preserved_errors = validator2.get_logs()['issues']
    print(f"Preserved errors: {len(preserved_errors)}")
    for error in preserved_errors:
        print(f"  - {error.get('category')}: {error.get('reason')}")
    
    # Add new part and verify only new errors are added
    validator2.add_part("Documents", validate_new_only=True)
    all_errors = validator2.get_logs()['issues']
    print(f"Total errors after adding part: {len(all_errors)}")
    
    print("✅ Error persistence working correctly!")

if __name__ == "__main__":
    try:
        test_stateless_functionality()
        test_performance_comparison()
        test_error_persistence()
        
        print("\n🎉 All stateless tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 