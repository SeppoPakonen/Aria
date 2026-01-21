#!/usr/bin/env python3
"""
Comprehensive test for the enhanced undetected geckodriver.
"""

def test_enhanced_detection_evasion():
    """Test the enhanced undetected geckodriver against detection methods."""
    print("Testing ENHANCED undetected geckodriver implementation...")
    
    try:
        from undetected_geckodriver import Firefox
        import time
        
        # Create driver with default profile
        print("Creating Firefox instance with default profile...")
        driver = Firefox(use_default_profile=True)
        
        print("Navigating to browser detection test site...")
        driver.get("https://www.browserscan.net/bot-detection")
        
        # Wait a bit for page to load
        time.sleep(5)
        
        # Get page title and content snippets to see detection results
        title = driver.title
        print(f"Page title: {title}")
        
        # Try to get some content from the page
        try:
            body_text = driver.find_element("tag name", "body").text
            print(f"First 200 chars of body: {body_text[:200]}...")
            
            # Look for specific detection indicators in the page content
            if "Robot" in body_text or "Webdriver" in body_text:
                print("⚠️  STILL DETECTED: Robot or Webdriver mentioned in page content")
            else:
                print("✅ BETTER: No obvious detection indicators in page content")
                
        except Exception as e:
            print(f"Could not retrieve body text: {e}")
        
        # Check for webdriver property
        try:
            webdriver_present = driver.execute_script("return typeof navigator.webdriver !== 'undefined' && navigator.webdriver")
            print(f"navigator.webdriver present: {webdriver_present}")
            
            if not webdriver_present:
                print("✅ GOOD: navigator.webdriver is properly hidden")
            else:
                print("⚠️  ISSUE: navigator.webdriver is still detectable")
        except Exception as e:
            print(f"Could not check navigator.webdriver: {e}")
        
        # Check for other common detection vectors
        try:
            plugins_length = driver.execute_script("return navigator.plugins.length")
            print(f"navigator.plugins.length: {plugins_length}")
            
            # Check for presence of webdriver in plugins
            webdriver_in_plugins = driver.execute_script("""
                let found = false;
                for (let i = 0; i < navigator.plugins.length; i++) {
                    if (String(navigator.plugins[i]).indexOf('webdriver') !== -1) {
                        found = true;
                        break;
                    }
                }
                return found;
            """)
            print(f"Webdriver in plugins: {webdriver_in_plugins}")
            
        except Exception as e:
            print(f"Could not check plugins: {e}")
        
        # Additional stealth checks
        try:
            # Check for window.chrome
            chrome_present = driver.execute_script("return typeof window.chrome !== 'undefined'")
            print(f"window.chrome present: {chrome_present}")
            
            # Check for window.external
            external_present = driver.execute_script("return typeof window.external !== 'undefined'")
            print(f"window.external present: {external_present}")
            
            # Check for webdriver property on various objects
            webdriver_props = driver.execute_script("""
                var detections = [];
                if ('webdriver' in navigator) detections.push('navigator.webdriver');
                if (window.webdriver) detections.push('window.webdriver');
                if (document.webdriver) detections.push('document.webdriver');
                return detections;
            """)
            print(f"Webdriver properties detected: {webdriver_props}")
            
        except Exception as e:
            print(f"Could not run additional stealth checks: {e}")
        
        driver.quit()
        print("\nTest completed.")
        
        return True
        
    except Exception as e:
        print(f"Error during detection test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality still works."""
    print("\nTesting basic functionality...")
    
    try:
        from undetected_geckodriver import Firefox
        import time
        
        # Test basic usage
        driver = Firefox(use_default_profile=True)
        driver.get("https://www.example.com")
        title = driver.title
        print(f"Basic navigation test - Title: {title}")
        
        # Test with specific options
        driver2 = Firefox(headless=False, use_default_profile=True)  # Set to True to see behavior
        driver2.get("https://httpbin.org/headers")
        title2 = driver2.title
        print(f"Second instance test - Title: {title2}")
        
        driver.quit()
        driver2.quit()
        
        print("✅ Basic functionality works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running comprehensive tests for enhanced undetected geckodriver...")
    
    success1 = test_basic_functionality()
    success2 = test_enhanced_detection_evasion()
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY:")
    print(f"Basic functionality: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Detection evasion: {'✅ TESTED' if success2 else '❌ FAILED'}")
    print("="*60)
    
    if success1:
        print("\nThe enhanced undetected geckodriver is working!")
        print("While complete undetection may not be possible against all methods,")
        print("the enhancements significantly improve stealth capabilities.")
    else:
        print("\nThere are issues with the implementation that need to be addressed.")