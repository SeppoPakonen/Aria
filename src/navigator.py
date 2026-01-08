import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class AriaNavigator:
    def __init__(self, headless=False):
        options = Options()
        if headless:
            options.add_argument("--headless")
        
        # Initialize Chrome Driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    def navigate(self, url):
        print(f"Navigating to: {url}")
        self.driver.get(url)

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    # Basic smoke test
    navigator = AriaNavigator(headless=False)
    try:
        navigator.navigate("https://www.google.com")
        print(f"Page title: {navigator.driver.title}")
    finally:
        navigator.close()
