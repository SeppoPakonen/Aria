#!/usr/bin/env python3
"""
Test script to verify that undetected geckodriver is working properly.
"""

import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all necessary modules can be imported."""
    print("Testing imports...")
    
    try:
        from undetected_geckodriver import Firefox as UndetectedFirefox
        print("✓ Successfully imported undetected_geckodriver.Firefox")
    except ImportError as e:
        print(f"✗ Failed to import undetected_geckodriver: {e}")
        return False
        
    try:
        from src.navigator import AriaNavigator
        print("✓ Successfully imported AriaNavigator")
    except ImportError as e:
        print(f"✗ Failed to import AriaNavigator: {e}")
        return False
        
    try:
        from src.undetected_firefox import Firefox, Options, Profile
        print("✓ Successfully imported undetected_firefox components")
    except ImportError as e:
        print(f"✗ Failed to import undetected_firefox components: {e}")
        return False
    
    return True

def test_basic_usage():
    """Test basic usage of undetected geckodriver."""
    print("\nTesting basic usage...")
    
    try:
        from undetected_geckodriver import Firefox
        driver = Firefox()
        print("✓ Successfully created Firefox instance with undetected geckodriver")
        
        # Test navigating to a page
        driver.get("https://www.httpbin.org/headers")
        print(f"✓ Successfully navigated, page title: {driver.title[:50]}...")
        
        # Close the browser
        driver.quit()
        print("✓ Successfully closed the browser")
        
        return True
    except Exception as e:
        print(f"✗ Error during basic usage test: {e}")
        return False

def test_navigator_integration():
    """Test integration with the AriaNavigator."""
    print("\nTesting navigator integration...")
    
    try:
        from src.navigator import AriaNavigator
        from undetected_geckodriver import Firefox as UndetectedFirefox
        
        # Check if undetected geckodriver is available
        navigator = AriaNavigator()
        
        # Check the UNDETECTED_GECKODRIVER_AVAILABLE flag
        if hasattr(navigator, 'UNDETECTED_GECKODRIVER_AVAILABLE'):
            print(f"✓ UNDETECTED_GECKODRIVER_AVAILABLE flag exists: {navigator.UNDETECTED_GECKODRIVER_AVAILABLE}")
        else:
            # Check if it's available in the module level
            import src.navigator as nav_module
            if hasattr(nav_module, 'UNDETECTED_GECKODRIVER_AVAILABLE'):
                print(f"✓ UNDETECTED_GECKODRIVER_AVAILABLE flag exists: {nav_module.UNDETECTED_GECKODRIVER_AVAILABLE}")
            else:
                print("? UNDETECTED_GECKODRIVER_AVAILABLE flag not found (this may be OK)")
        
        return True
    except Exception as e:
        print(f"✗ Error during navigator integration test: {e}")
        return False

def main():
    """Run all tests."""
    print("Running undetected geckodriver tests...\n")
    
    success = True
    success &= test_imports()
    success &= test_basic_usage()
    success &= test_navigator_integration()
    
    print(f"\n{'='*50}")
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())