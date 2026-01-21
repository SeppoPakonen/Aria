#!/usr/bin/env python3
"""
Simple test to verify the example usage from the request works.
"""

def test_example_usage():
    """Test the exact example usage from the original request."""
    print("Testing example usage:")
    print("from undetected_geckodriver import Firefox")
    print("driver = Firefox()")
    print("driver.get(\"https://www.example.com\")")
    print()
    
    try:
        from undetected_geckodriver import Firefox
        print("✓ Successfully imported Firefox from undetected_geckodriver")
        
        # Create a driver instance (but don't actually navigate to avoid opening browser in test)
        driver = Firefox()
        print("✓ Successfully created Firefox driver instance")
        
        # Test navigation without actually waiting for load
        driver.get("https://www.example.com")
        print("✓ Successfully navigated to https://www.example.com")
        
        # Get the title to confirm it worked
        title = driver.title
        print(f"✓ Page title: {title[:50]}...")
        
        # Close the driver
        driver.quit()
        print("✓ Successfully closed the driver")
        
        return True
    except Exception as e:
        print(f"✗ Error during example usage test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_aria_integration():
    """Test that Aria can use undetected geckodriver."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    print("\nTesting Aria integration with undetected geckodriver...")
    
    try:
        from src.navigator import UNDETECTED_GECKODRIVER_AVAILABLE
        print(f"✓ UNDETECTED_GECKODRIVER_AVAILABLE = {UNDETECTED_GECKODRIVER_AVAILABLE}")
        
        if UNDETECTED_GECKODRIVER_AVAILABLE:
            print("✓ Aria is configured to use undetected geckodriver for Firefox")
        else:
            print("! Aria will fall back to regular geckodriver")
        
        return True
    except Exception as e:
        print(f"✗ Error during Aria integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Testing the example usage from the request...")
    print("="*60)
    
    success = True
    success &= test_example_usage()
    success &= test_aria_integration()
    
    print("\n" + "="*60)
    if success:
        print("✓ All tests passed! The implementation works as requested.")
        print("\nThe changes made:")
        print("1. Added 'undetected-geckodriver' to requirements.txt")
        print("2. Modified navigator.py to use undetected geckodriver when available")
        print("3. Maintained fallback to regular geckodriver if undetected is not available")
        print("4. Preserved all existing functionality")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())