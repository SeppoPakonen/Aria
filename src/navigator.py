import os
import json
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

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
from logger import get_logger

logger = get_logger("navigator")

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

    def start_session(self, browser_name="chrome", headless=False, force=False):
        logger.info(f"Starting browser session: {browser_name} (headless={headless}, force={force})")
        session_file = self.get_session_file_path()
        if os.path.exists(session_file):
            if self.connect_to_session():
                if force:
                    print("Closing active session to start a new one...")
                    logger.info("Closing active session due to force=True")
                    self.close_session()
                else:
                    print("An Aria session is already active.")
                    logger.warning("Attempted to start session while one is already active.")
                    return None
            else:
                logger.info("Cleaning up stale session file.")
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
                logger.error(f"Unsupported browser: {browser_name}")
                return None

            # Try to get the remote URL in a way that works across Selenium versions
            remote_url = None
            if hasattr(self.driver.command_executor, "_url"):
                remote_url = self.driver.command_executor._url
            elif hasattr(self.driver.command_executor, "_client_config"):
                remote_url = self.driver.command_executor._client_config.remote_server_addr
            
            session_data = {
                "session_id": self.driver.session_id,
                "url": remote_url,
                "browser": browser_name
            }

            with open(session_file, "w") as f:
                json.dump(session_data, f)
            
            print(f"Aria session started with ID: {self.driver.session_id} using {browser_name}")
            logger.info(f"Session started: {self.driver.session_id}")
            return self.driver
        except WebDriverException as e:
            print(f"Error starting browser session: {e}")
            logger.error(f"WebDriverException during start_session: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logger.error(f"Unexpected error during start_session: {e}")
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
            logger.warning("Attempted navigation without active session.")
            return

        try:
            print(f"Navigating to: {url}")
            logger.info(f"Navigating to URL: {url}")
            self.driver.get(url)
        except WebDriverException as e:
            print(f"Error navigating to {url}: {e}")
            logger.error(f"WebDriverException during navigation to {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during navigation: {e}")
            logger.error(f"Unexpected error during navigation to {url}: {e}")

    def close_session(self):
        logger.info("Closing browser session.")
        session_file = self.get_session_file_path()
        if not os.path.exists(session_file):
            print("No active Aria session found.")
            logger.warning("Attempted to close session but no session file found.")
            return
        
        driver = self.connect_to_session()

        if driver:
            try:
                driver.quit()
                logger.info("Browser session closed successfully.")
            except WebDriverException as e:
                print(f"Error while closing the browser session: {e}")
                logger.error(f"WebDriverException during close_session: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while closing the session: {e}")
                logger.error(f"Unexpected error during close_session: {e}")

        if os.path.exists(session_file):
            os.remove(session_file)
        
        print("Aria session closed.")

    def list_tabs(self):
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            return []

        tabs = []
        original_window = self.driver.current_window_handle

        try:
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                tabs.append({
                    "title": self.driver.title,
                    "url": self.driver.current_url
                })
            # Switch back to the original window
            self.driver.switch_to.window(original_window)
        except WebDriverException as e:
            print(f"Error listing tabs: {e}")
            return []
        
        return tabs

    def goto_tab(self, identifier):
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            print("No active session. Use 'aria open' to start a session.")
            return False

        try:
            handles = self.driver.window_handles
            if isinstance(identifier, int):
                if 1 <= identifier <= len(handles):
                    self.driver.switch_to.window(handles[identifier - 1])
                    return True
                else:
                    print(f"Invalid tab index: {identifier}")
                    return False
            
            elif isinstance(identifier, str):
                original_window = self.driver.current_window_handle
                for handle in handles:
                    self.driver.switch_to.window(handle)
                    if self.driver.title == identifier:
                        return True
                # If not found, switch back to original window
                self.driver.switch_to.window(original_window)
                print(f"Tab with title '{identifier}' not found.")
                return False
        except WebDriverException as e:
            print(f"Error going to tab: {e}")
            return False
        
        return False

    def get_page_content(self):
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            print("No active session. Use 'aria open' to start a session.")
            return ""

        try:
            return self.driver.find_element(By.TAG_NAME, 'body').text
        except WebDriverException as e:
            print(f"Error getting page content: {e}")
            return ""
