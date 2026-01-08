import os
import json
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

# Webdriver managers
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Webdriver services
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

# Webdriver options
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

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

    def start_session(self, browser_name="chrome", headless=False):
        session_file = self.get_session_file_path()
        if os.path.exists(session_file):
            if self.connect_to_session():
                print("An Aria session is already active.")
                return None
            else:
                os.remove(session_file)

        try:
            if browser_name == "chrome":
                options = ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                self.driver = webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=options
                )
            elif browser_name == "firefox":
                options = FirefoxOptions()
                if headless:
                    options.add_argument("--headless")
                self.driver = webdriver.Firefox(
                    service=FirefoxService(GeckoDriverManager().install()),
                    options=options
                )
            elif browser_name == "edge":
                options = EdgeOptions()
                if headless:
                    options.add_argument("--headless")
                self.driver = webdriver.Edge(
                    service=EdgeService(EdgeChromiumDriverManager().install()),
                    options=options
                )
            else:
                print(f"Browser '{browser_name}' is not supported.")
                return None

            session_data = {
                "session_id": self.driver.session_id,
                "url": self.driver.command_executor._url,
                "browser": browser_name
            }

            with open(session_file, "w") as f:
                json.dump(session_data, f)
            
            print(f"Aria session started with ID: {self.driver.session_id} using {browser_name}")
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

            browser_name = session_data.get("browser", "chrome")
            
            if browser_name == "chrome":
                options = ChromeOptions()
            elif browser_name == "firefox":
                options = FirefoxOptions()
            elif browser_name == "edge":
                options = EdgeOptions()
            else:
                # Should not happen if session file is valid
                return None

            driver = webdriver.Remote(
                command_executor=session_data["url"],
                options=options
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