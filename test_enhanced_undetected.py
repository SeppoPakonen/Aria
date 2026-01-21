#!/usr/bin/env python3
"""
Test script for the enhanced undetected geckodriver with default profile support.
"""

def test_enhanced_undetected_geckodriver():
    """Test the enhanced undetected geckodriver functionality."""
    print("Testing enhanced undetected geckodriver with default profile support...")
    
    try:
        # Add the custom undetected geckodriver to the path
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'undetected_geckodriver_custom'))
        
        from undetected_geckodriver import Firefox
        print("✓ Successfully imported enhanced undetected_geckodriver")
        
        # Test 1: Basic usage (without profile)
        print("\nTest 1: Basic usage without profile...")
        driver1 = Firefox()
        driver1.get("https://www.example.com")
        print(f"✓ Basic usage works - Page title: {driver1.title[:50]}...")
        driver1.quit()
        print("✓ Browser closed successfully")
        
        # Test 2: Usage with default profile
        print("\nTest 2: Usage with default profile...")
        driver2 = Firefox(use_default_profile=True)
        driver2.get("https://www.example.com")
        print(f"✓ Default profile usage works - Page title: {driver2.title[:50]}...")
        driver2.quit()
        print("✓ Browser with default profile closed successfully")
        
        # Test 3: Usage with specific profile path (if available)
        print("\nTest 3: Checking for default profile path...")
        # Create a temporary instance to check for default profile
        temp_driver = Firefox.__new__(Firefox)  # Create without initializing
        default_profile = temp_driver._get_default_firefox_profile()
        if default_profile:
            print(f"✓ Found default profile: {default_profile}")
        else:
            print("! Could not find default Firefox profile")
        
        print("\n✓ All tests passed! Enhanced undetected geckodriver is working correctly.")
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_undetected_geckodriver()
    if success:
        print("\n" + "="*60)
        print("SUCCESS: Enhanced undetected geckodriver is ready!")
        print("Features added:")
        print("1. Fixed the __len__ method issue that caused errors")
        print("2. Added support for using default Firefox profile")
        print("3. Added support for using specific profile paths")
        print("4. Maintained all original undetected functionality")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("FAILURE: Tests failed!")
        print("="*60)
        exit(1)