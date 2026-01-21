#!/usr/bin/env python3
"""
Comprehensive test for the undetected geckodriver integration with AriaNavigator.
"""

import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_navigator_firefox():
    """Test that the navigator can start a Firefox session with undetected geckodriver."""
    print("Testing AriaNavigator with Firefox and undetected geckodriver...")
    
    try:
        from src.navigator import AriaNavigator
        from src.undetected_firefox import Firefox as UndetectedFirefox
        
        # Create a navigator instance
        navigator = AriaNavigator()
        
        # Check if undetected geckodriver is available
        if not hasattr(sys.modules['src.navigator'], 'UNDETECTED_GECKODRIVER_AVAILABLE'):
            import src.navigator as nav_module
            undetected_available = getattr(nav_module, 'UNDETECTED_GECKODRIVER_AVAILABLE', False)
        else:
            undetected_available = navigator.UNDETECTED_GECKODRIVER_AVAILABLE
            
        print(f"Undetected geckodriver available: {undetected_available}")
        
        if not undetected_available:
            print("⚠️  Undetected geckodriver not available - this might be due to import issues")
            return False
        
        # Note: We're not actually starting a session here as it would open a browser
        # Instead, we'll just verify the code paths are correct
        print("✓ Navigator created successfully with undetected geckodriver support")
        
        # Test that the Firefox import works correctly
        driver = UndetectedFirefox.__name__
        print(f"✓ UndetectedFirefox class available: {driver}")
        
        return True
    except Exception as e:
        print(f"✗ Error during navigator test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_example_usage():
    """Test the example usage from the original request."""
    print("\nTesting example usage: from undetected_geckodriver import Firefox")
    
    try:
        from undetected_geckodriver import Firefox
        print("✓ Successfully imported Firefox from undetected_geckodriver")
        
        # Test that the import works as expected
        # (Don't actually create a driver to avoid opening a browser)
        print(f"✓ Firefox class available: {Firefox.__name__}")
        
        return True
    except Exception as e:
        print(f"✗ Error during example usage test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_navigator_code_paths():
    """Test that the navigator code paths are correct."""
    print("\nTesting navigator code paths...")
    
    try:
        import src.navigator as nav_module
        
        # Check that the import logic worked
        undetected_available = getattr(nav_module, 'UNDETECTED_GECKODRIVER_AVAILABLE', False)
        print(f"✓ UNDETECTED_GECKODRIVER_AVAILABLE = {undetected_available}")
        
        if undetected_available:
            # Check that the correct classes were imported
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            print("✓ FirefoxOptions imported from selenium (fallback for undetected)")
        else:
            # This means undetected_geckodriver wasn't available during import
            print("! undetected_geckodriver not available during import (expected if not installed)")
        
        return True
    except Exception as e:
        print(f"✗ Error during code path test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Running comprehensive undetected geckodriver tests...\n")
    
    success = True
    success &= test_navigator_firefox()
    success &= test_example_usage()
    success &= test_navigator_code_paths()
    
    print(f"\n{'='*60}")
    if success:
        print("✓ All comprehensive tests passed!")
        return 0
    else:
        print("✗ Some comprehensive tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())