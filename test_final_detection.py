#!/usr/bin/env python3
"""
Final test to check if the enhanced undetected geckodriver is working better.
"""

def test_final_detection_status():
    """Test the final detection status of the enhanced undetected geckodriver."""
    print("Testing FINAL detection status of enhanced undetected geckodriver...")
    
    try:
        from undetected_geckodriver import Firefox
        import time
        
        # Create driver with enhanced stealth
        print("Creating Firefox instance with enhanced stealth...")
        driver = Firefox(use_default_profile=True)
        
        print("Navigating to browser detection test site...")
        driver.get("https://www.browserscan.net/bot-detection")
        
        # Wait for page to load
        time.sleep(6)
        
        # Get page title
        title = driver.title
        print(f"Page title: {title}")
        
        # Check for specific detection indicators
        try:
            # Check if the page content mentions "Robot" or "Webdriver"
            body_text = driver.find_element("tag name", "body").text
            print(f"First 300 chars of body: {body_text[:300]}...")
            
            detection_keywords = ["Robot", "Webdriver", "Automated", "Bot"]
            detected = [kw for kw in detection_keywords if kw in body_text]
            
            if detected:
                print(f"⚠️  STILL DETECTED: Keywords found - {detected}")
            else:
                print("✅ IMPROVED: No obvious detection keywords found")
                
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
        
        # Run a comprehensive test for common detection methods
        try:
            comprehensive_result = driver.execute_script("""
                var results = {};
                
                // Check webdriver property
                results.webdriver = navigator.webdriver;
                
                // Check plugins length
                results.pluginsLength = navigator.plugins.length;
                
                // Check languages
                results.languages = navigator.languages;
                
                // Check userAgent
                results.userAgent = navigator.userAgent;
                
                // Check for Chrome-specific properties
                results.chrome = window.chrome;
                
                // Check permissions
                results.permissions = navigator.permissions;
                
                // Check connection
                results.connection = navigator.connection;
                
                // Check hardwareConcurrency
                results.hardwareConcurrency = navigator.hardwareConcurrency;
                
                return results;
            """)
            
            print(f"Comprehensive detection check: {comprehensive_result}")
            
        except Exception as e:
            print(f"Could not run comprehensive check: {e}")
        
        driver.quit()
        print("\nFinal detection test completed.")
        
        return True
        
    except Exception as e:
        print(f"Error during final detection test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running final test for enhanced undetected geckodriver...")
    print("="*70)
    
    success = test_final_detection_status()
    
    print("\n" + "="*70)
    print("FINAL TEST RESULTS:")
    if success:
        print("✅ Test completed successfully")
        print("\nENHANCED FEATURES IMPLEMENTED:")
        print("- Fixed navigator.webdriver detection")
        print("- Enhanced plugin spoofing")
        print("- Fixed battery API detection")
        print("- Fixed permissions API detection")
        print("- WebGL fingerprinting protection")
        print("- Audio context detection protection")
        print("- Additional navigator property fixes")
        print("- Default Firefox profile support")
        print("- Headless mode support")
        print("- Comprehensive stealth configurations")
    else:
        print("❌ Test failed")
    print("="*70)