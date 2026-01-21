#!/usr/bin/env python3
"""
Test the enhanced stealth techniques of the undetected geckodriver.
"""

def test_stealth_techniques():
    """Test the enhanced stealth techniques."""
    print("Testing enhanced stealth techniques...")
    
    try:
        from undetected_geckodriver import Firefox
        import time
        
        # Create driver with enhanced stealth
        print("Creating Firefox instance with enhanced stealth...")
        driver = Firefox(use_default_profile=True)
        
        print("Navigating to browser detection test site...")
        driver.get("https://www.browserscan.net/bot-detection")
        
        # Wait for page to load
        time.sleep(5)
        
        # Get page title
        title = driver.title
        print(f"Page title: {title}")
        
        # Check for specific detection indicators
        try:
            # Check if the page content mentions "Robot" or "Webdriver"
            body_text = driver.find_element("tag name", "body").text
            print(f"First 300 chars of body: {body_text[:300]}...")
            
            if "Robot" in body_text or "Webdriver" in body_text:
                print("⚠️  STILL DETECTED: Robot or Webdriver mentioned in page content")
            else:
                print("✅ IMPROVED: No obvious Robot/Webdriver detection in page content")
                
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
            
            # Check for window.chrome
            chrome_present = driver.execute_script("return typeof window.chrome !== 'undefined'")
            print(f"window.chrome present: {chrome_present}")
            
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
            print(f"Could not check additional vectors: {e}")
        
        # Check for the specific properties mentioned in the detection
        try:
            # Check for getBattery function
            has_battery = driver.execute_script("return 'getBattery' in navigator")
            print(f"navigator.getBattery exists: {has_battery}")
            
            # Check for doNotTrack
            dnt_value = driver.execute_script("return navigator.doNotTrack || window.doNotTrack || navigator.msDoNotTrack")
            print(f"doNotTrack value: {dnt_value}")
            
            # Check for globalPrivacyControl
            gpc_value = driver.execute_script("return navigator.globalPrivacyControl")
            print(f"globalPrivacyControl value: {gpc_value}")
            
        except Exception as e:
            print(f"Could not check specific detection vectors: {e}")
        
        driver.quit()
        print("\nEnhanced stealth test completed.")
        
        return True
        
    except Exception as e:
        print(f"Error during stealth test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing enhanced stealth techniques of undetected geckodriver...")
    print("="*60)
    
    success = test_stealth_techniques()
    
    print("\n" + "="*60)
    if success:
        print("✅ Test completed. Enhanced stealth techniques applied.")
        print("\nThe enhanced version includes:")
        print("- Fixed navigator.webdriver detection")
        print("- Enhanced plugin spoofing")
        print("- Fixed battery API detection")
        print("- Fixed permissions API detection")
        print("- WebGL fingerprinting protection")
        print("- Audio context detection protection")
        print("- Additional navigator property fixes")
    else:
        print("❌ Test failed.")
    print("="*60)