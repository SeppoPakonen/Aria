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

class ReusableRemote(webdriver.Remote):
    def __init__(self, command_executor, options, session_id):
        self._session_id = session_id
        super().__init__(command_executor=command_executor, options=options)
        self.session_id = session_id

    def start_session(self, capabilities, browser_profile=None):
        # Override to prevent starting a new session
        if hasattr(self, "_session_id") and self._session_id:
            self.session_id = self._session_id
        else:
            super().start_session(capabilities, browser_profile)

class AriaNavigator:
    def __init__(self):
        self.driver: WebDriver | None = None

    def get_session_file_path(self, browser_name=None):
        temp_dir = os.path.join(os.path.expanduser("~"), ".aria")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        if browser_name:
            return os.path.join(temp_dir, f"aria_session_{browser_name}.json")
        return os.path.join(temp_dir, "aria_session_current.json")

    def _save_session(self, browser_name, session_data):
        # Save browser-specific session
        with open(self.get_session_file_path(browser_name), "w") as f:
            json.dump(session_data, f)
        # Set as current session
        with open(self.get_session_file_path(), "w") as f:
            json.dump({"browser": browser_name}, f)

    def _get_current_browser(self):
        current_file = self.get_session_file_path()
        if os.path.exists(current_file):
            try:
                with open(current_file, "r") as f:
                    return json.load(f).get("browser")
            except:
                pass
        return None

    def _load_session_data(self, browser_name):
        session_file = self.get_session_file_path(browser_name)
        if os.path.exists(session_file):
            with open(session_file, "r") as f:
                return json.load(f)
        return None

    def start_session(self, browser_name="chrome", headless=False, force=False):
        logger.info(f"Starting browser session: {browser_name} (headless={headless}, force={force})")
        session_file = self.get_session_file_path(browser_name)
        
        if os.path.exists(session_file):
            if self.connect_to_session(browser_name):
                if force:
                    print(f"Closing active {browser_name} session to start a new one...")
                    self.close_session(browser_name)
                else:
                    print(f"An Aria session for {browser_name} is already active.")
                    # Still set it as current
                    self._save_session(browser_name, self._load_session_data(browser_name))
                    return self.driver
            else:
                os.remove(session_file)

        try:
            import subprocess
            import time
            import socket

            def find_free_port():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', 0))
                    return s.getsockname()[1]

            port = find_free_port()
            
            driver_path = None
            options = None
            if browser_name == "chrome":
                driver_path = ChromeDriverManager().install()
                options = ChromeOptions()
            elif browser_name == "firefox":
                driver_path = GeckoDriverManager().install()
                options = FirefoxOptions()
            elif browser_name == "edge":
                driver_path = EdgeChromiumDriverManager().install()
                options = EdgeOptions()
            else:
                print(f"Browser '{browser_name}' is not supported.")
                return None

            creation_flags = 0
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            
            proc = subprocess.Popen([driver_path, f"--port={port}"], creationflags=creation_flags)
            time.sleep(2)
            
            if headless:
                options.add_argument("--headless")
            
            remote_url = f"http://localhost:{port}"
            self.driver = webdriver.Remote(command_executor=remote_url, options=options)
            
            session_data = {
                "session_id": self.driver.session_id,
                "url": remote_url,
                "browser": browser_name,
                "driver_pid": proc.pid
            }

            self._save_session(browser_name, session_data)
            
            print(f"Aria session started for {browser_name}")
            return self.driver
        except Exception as e:
            print(f"Error starting {browser_name} session: {e}")
            return None

    def connect_to_session(self, browser_name=None):
        if not browser_name:
            browser_name = self._get_current_browser()
        
        if not browser_name:
            # Fallback: pick any active browser
            active = self.list_active_browsers()
            if active:
                browser_name = active[0]
            else:
                return None

        session_data = self._load_session_data(browser_name)
        if not session_data:
            return None

        try:
            if browser_name == "chrome":
                options = ChromeOptions()
            elif browser_name == "firefox":
                options = FirefoxOptions()
            elif browser_name == "edge":
                options = EdgeOptions()
            else:
                return None

            driver = ReusableRemote(
                command_executor=session_data["url"],
                options=options,
                session_id=session_data["session_id"]
            )
            # Verify it works
            _ = driver.current_url
            self.driver = driver
            # Update current browser
            with open(self.get_session_file_path(), "w") as f:
                json.dump({"browser": browser_name}, f)
            return self.driver
        except Exception as e:
            logger.error(f"Failed to connect to {browser_name} session: {e}")
            session_file = self.get_session_file_path(browser_name)
            if os.path.exists(session_file):
                os.remove(session_file)
            return None

    def list_active_browsers(self):
        temp_dir = os.path.join(os.path.expanduser("~"), ".aria")
        browsers = []
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                if f.startswith("aria_session_") and f.endswith(".json") and f != "aria_session_current.json":
                    browser_name = f[len("aria_session_"):-len(".json")]
                    browsers.append(browser_name)
        return browsers

    def close_session(self, browser_name=None):
        if not browser_name:
            # Close all
            browsers = self.list_active_browsers()
            for b in browsers:
                self.close_session(b)
            return

        logger.info(f"Closing {browser_name} session.")
        session_file = self.get_session_file_path(browser_name)
        session_data = self._load_session_data(browser_name)
        
        if session_data:
            driver_pid = session_data.get("driver_pid")
            try:
                # Try to quit driver gracefully
                if browser_name == "chrome":
                    options = ChromeOptions()
                elif browser_name == "firefox":
                    options = FirefoxOptions()
                elif browser_name == "edge":
                    options = EdgeOptions()
                
                driver = webdriver.Remote(command_executor=session_data["url"], options=options)
                driver.session_id = session_data["session_id"]
                driver.quit()
            except:
                pass

            if driver_pid:
                import subprocess
                try:
                    if os.name == 'nt':
                        subprocess.run(['taskkill', '/F', '/T', '/PID', str(driver_pid)], capture_output=True)
                    else:
                        import signal
                        os.kill(driver_pid, signal.SIGTERM)
                except:
                    pass

        if os.path.exists(session_file):
            os.remove(session_file)
        
        # If we closed the current browser, clear current_session.json
        if self._get_current_browser() == browser_name:
            current_file = self.get_session_file_path()
            if os.path.exists(current_file):
                os.remove(current_file)
        
        print(f"Aria session for {browser_name} closed.")

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

    def navigate_with_prompt(self, prompt):
        """Uses AI to determine where to navigate based on a prompt."""
        logger.info(f"Navigating with prompt: {prompt}")
        # In a real implementation, this would call Gemini to get a URL or perform a search.
        # For now, we'll just do a search on DuckDuckGo as a heuristic.
        import urllib.parse
        search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(prompt)}"
        self.navigate(search_url)
        print(f"Heuristic: Searching for '{prompt}' on DuckDuckGo.")

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
                    "id": handle,
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
            # 1. Try by handle (tab_id)
            if identifier in handles:
                self.driver.switch_to.window(identifier)
                return True

            # 2. Try by index (0-based)
            try:
                idx = int(identifier)
                if 0 <= idx < len(handles):
                    self.driver.switch_to.window(handles[idx])
                    return True
            except (ValueError, TypeError):
                pass
            
            # 3. Try by title
            original_window = self.driver.current_window_handle
            for handle in handles:
                self.driver.switch_to.window(handle)
                if self.driver.title == identifier:
                    return True
            
            # If not found, switch back to original window
            self.driver.switch_to.window(original_window)
            print(f"Tab with identifier '{identifier}' not found.")
            return False
        except WebDriverException as e:
            print(f"Error going to tab: {e}")
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

    def get_tabs_content(self, identifiers):
        """Retrieves content from multiple tabs.
        identifiers: list of tab indices, IDs, or titles.
        Returns a list of dicts: {'identifier': ..., 'content': ..., 'title': ..., 'url': ...}
        """
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            print("No active session. Use 'aria open' to start a session.")
            return []

        original_window = self.driver.current_window_handle
        results = []
        
        for identifier in identifiers:
            if self.goto_tab(identifier):
                content = self.get_page_content()
                results.append({
                    "identifier": identifier,
                    "title": self.driver.title,
                    "url": self.driver.current_url,
                    "content": content
                })
            else:
                logger.warning(f"Could not switch to tab '{identifier}' to get content.")
        
        # Switch back to the original window
        self.driver.switch_to.window(original_window)
        return results

    def new_tab(self, url="about:blank"):
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            print("No active session. Use 'aria open' to start a session.")
            return False

        try:
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            # Switch to the new window
            self.driver.switch_to.window(self.driver.window_handles[-1])
            logger.info(f"Opened new tab with URL: {url}")
            return True
        except WebDriverException as e:
            print(f"Error opening new tab: {e}")
            logger.error(f"WebDriverException during new_tab: {e}")
            return False