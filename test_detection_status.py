#!/usr/bin/env python3
"""
Test script to check if the undetected geckodriver is truly undetectable.
"""

def test_detection():
    """Test the current undetected geckodriver against detection methods."""
    print("Testing current undetected geckodriver implementation...")
    
    try:
        from undetected_geckodriver import Firefox
        import time
        
        # Create driver with default profile
        driver = Firefox(use_default_profile=True)
        
        print("Navigating to browser detection test site...")
        driver.get("https://www.browserscan.net/bot-detection")
        
        # Wait a bit for page to load
        time.sleep(3)
        
        # Get page title and content snippets to see detection results
        title = driver.title
        print(f"Page title: {title}")
        
        # Try to get some content from the page
        try:
            body_text = driver.find_element("tag name", "body").text
            print(f"First 200 chars of body: {body_text[:200]}...")
        except:
            print("Could not retrieve body text")
        
        # Check for webdriver property
        try:
            webdriver_present = driver.execute_script("return typeof navigator.webdriver !== 'undefined'")
            print(f"navigator.webdriver present: {webdriver_present}")
        except Exception as e:
            print(f"Could not check navigator.webdriver: {e}")
        
        # Check for other common detection vectors
        try:
            plugins_length = driver.execute_script("return navigator.plugins.length")
            print(f"navigator.plugins.length: {plugins_length}")
        except Exception as e:
            print(f"Could not check plugins length: {e}")
        
        driver.quit()
        print("Test completed.")
        
    except Exception as e:
        print(f"Error during detection test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detection()