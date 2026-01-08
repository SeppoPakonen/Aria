import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webdriver import WebDriver

SESSION_FILE = "aria_session.json"

class AriaNavigator:
    def __init__(self):
        self.driver: WebDriver | None = None

    def get_session_file_path(self):
        # Using a folder in the user's home directory to store session state
        temp_dir = os.path.join(os.path.expanduser("~"), ".aria")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        return os.path.join(temp_dir, SESSION_FILE)

    def start_session(self, headless=False):
        session_file = self.get_session_file_path()
        if os.path.exists(session_file):
            # Check if the session is still active
            if self.connect_to_session():
                print("An Aria session is already active.")
                return None
            else:
                # Stale session file, remove it
                os.remove(session_file)

        options = Options()
        if headless:
            options.add_argument("--headless")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        session_data = {
            "session_id": self.driver.session_id,
            "url": self.driver.command_executor._url
        }

        with open(session_file, "w") as f:
            json.dump(session_data, f)
        
        print(f"Aria session started with ID: {self.driver.session_id}")
        return self.driver

    def connect_to_session(self):
        session_file = self.get_session_file_path()
        if not os.path.exists(session_file):
            return None

        with open(session_file, "r") as f:
            session_data = json.load(f)

        try:
            # Create a new WebDriver instance and attach to the existing session
            driver = webdriver.Remote(
                command_executor=session_data["url"],
                options=Options()
            )
            driver.session_id = session_data["session_id"]
            # Check if the session is still valid by getting the current URL
            _ = driver.current_url
            self.driver = driver
            return self.driver
        except Exception:
            # Session is not valid anymore
            os.remove(session_file)
            return None


    def navigate(self, url):
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            print("No active session. Use 'aria open' to start a session.")
            return

        print(f"Navigating to: {url}")
        self.driver.get(url)

    def close_session(self):
        session_file = self.get_session_file_path()
        if not os.path.exists(session_file):
            print("No active Aria session found.")
            return
        
        driver = self.connect_to_session()

        if driver:
            driver.quit()
        
        if os.path.exists(session_file):
            os.remove(session_file)
        
        print("Aria session closed.")