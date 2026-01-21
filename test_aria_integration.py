#!/usr/bin/env python3
"""
Test script to verify the Aria framework is using the enhanced undetected geckodriver.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_aria_with_enhanced_undetected():
    """Test that Aria is using the enhanced undetected geckodriver."""
    print("Testing Aria framework with enhanced undetected geckodriver...")
    
    try:
        from navigator import AriaNavigator
        from undetected_geckodriver import Firefox
        
        # Check if undetected geckodriver is available
        navigator = AriaNavigator()
        
        # Check if the UNDETECTED_GECKODRIVER_AVAILABLE flag is set correctly
        import src.navigator as nav_module
        undetected_available = getattr(nav_module, 'UNDETECTED_GECKODRIVER_AVAILABLE', False)
        
        print(f"✓ UNDETECTED_GECKODRIVER_AVAILABLE = {undetected_available}")
        
        if undetected_available:
            print("✓ Aria is configured to use enhanced undetected geckodriver")
            
            # Test creating an undetected Firefox instance directly
            driver = Firefox(use_default_profile=True)
            print(f"✓ Successfully created undetected Firefox instance")
            
            # Test navigation
            driver.get("https://www.example.com")
            print(f"✓ Successfully navigated - Title: {driver.title[:50]}...")
            
            # Close the driver
            driver.quit()
            print("✓ Successfully closed the driver")
            
            return True
        else:
            print("✗ Aria is not using undetected geckodriver")
            return False
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_usage():
    """Test direct usage of enhanced undetected geckodriver."""
    print("\nTesting direct usage of enhanced undetected geckodriver...")
    
    try:
        from undetected_geckodriver import Firefox
        
        # Test basic functionality
        driver = Firefox(use_default_profile=True)
        driver.get("https://www.httpbin.org/headers")
        title = driver.title
        print(f"✓ Direct usage works - Title: {title}")
        
        # Test with headless mode
        driver2 = Firefox(headless=True, use_default_profile=True)
        driver2.get("https://www.example.com")
        title2 = driver2.title
        print(f"✓ Headless mode works - Title: {title2}")
        
        driver.quit()
        driver2.quit()
        print("✓ Both instances closed successfully")
        
        return True
    except Exception as e:
        print(f"✗ Error during direct usage test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Aria framework integration with enhanced undetected geckodriver...")
    print("="*70)
    
    success1 = test_aria_with_enhanced_undetected()
    success2 = test_direct_usage()
    
    print("\n" + "="*70)
    print("TEST RESULTS:")
    print(f"Aria integration: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Direct usage: {'✅ PASS' if success2 else '❌ FAIL'}")
    print("="*70)
    
    if success1 and success2:
        print("\n🎉 SUCCESS: Aria framework is now using the enhanced undetected geckodriver!")
        print("The enhanced version includes:")
        print("- Fixed __len__ and __str__ method issues")
        print("- Default Firefox profile support")
        print("- Headless mode support") 
        print("- Comprehensive stealth configurations")
        print("- Better detection evasion")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")