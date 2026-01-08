import os
import json
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
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
            if self.connect_to_session():
                print("An Aria session is already active.")
                return None
            else:
                os.remove(session_file)

        try:
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
        except WebDriverException as e:
            print(f"Error starting browser session: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def connect_to_session(self):
        session_file = self.get_session_file_path()
        if not os.path.exists(session_file):
            return None

        try:
            with open(session_file, "r") as f:
                session_data = json.load(f)

            driver = webdriver.Remote(
                command_executor=session_data["url"],
                options=Options()
            )
            driver.session_id = session_data["session_id"]
            _ = driver.current_url
            self.driver = driver
            return self.driver
        except (WebDriverException, FileNotFoundError):
            os.remove(session_file)
            return None
        except Exception:
            os.remove(session_file)
            return None

    def navigate(self, url):
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            print("No active session. Use 'aria open' to start a session.")
            return

        try:
            print(f"Navigating to: {url}")
            self.driver.get(url)
        except WebDriverException as e:
            print(f"Error navigating to {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during navigation: {e}")

    def close_session(self):
        session_file = self.get_session_file_path()
        if not os.path.exists(session_file):
            print("No active Aria session found.")
            return
        
        driver = self.connect_to_session()

        if driver:
            try:
                driver.quit()
            except WebDriverException as e:
                print(f"Error while closing the browser session: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while closing the session: {e}")

        if os.path.exists(session_file):
            os.remove(session_file)
        
        print("Aria session closed.")
