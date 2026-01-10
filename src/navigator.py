import os
import json
import re
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
from logger import get_logger, time_it
from exceptions import BrowserError, SessionError, NavigationError
import time

logger = get_logger("navigator")

def retry_on_browser_error(retries=3, initial_delay=1, backoff_factor=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            from selenium.common.exceptions import WebDriverException
            last_exception = None
            current_delay = initial_delay
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except (WebDriverException, BrowserError) as e:
                    last_exception = e
                    if i < retries - 1:
                        logger.warning(
                            f"Browser operation failed (attempt {i+1}/{retries}). Retrying in {current_delay}s...",
                            extra={
                                "attempt": i + 1,
                                "max_retries": retries,
                                "delay": current_delay,
                                "error": str(e),
                                "function": func.__name__
                            }
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(
                            f"Browser operation failed after {retries} attempts.",
                            extra={
                                "max_retries": retries,
                                "error": str(e),
                                "function": func.__name__
                            }
                        )
            raise last_exception
        return wrapper
    return decorator

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
        self.throttle_delay = float(os.environ.get("ARIA_THROTTLE_DELAY", 0.0))
        self.randomize_delay = os.environ.get("ARIA_RANDOMIZE_DELAY", "true").lower() == "true"
        self.plugin_manager = None

    def throttle(self):
        """Introduces a delay based on throttle settings."""
        if self.throttle_delay > 0:
            import time
            import random
            delay = self.throttle_delay
            if self.randomize_delay:
                # Randomize +/- 20%
                delay = delay * random.uniform(0.8, 1.2)
            
            logger.info(f"Throttling for {delay:.2f}s", extra={"delay": delay})
            time.sleep(delay)

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

    def tag_tab(self, identifier, tag):
        """Adds a tag to a tab."""
        if not self.driver:
            self.driver = self.connect_to_session()
        if not self.driver:
            return False

        if self.goto_tab(identifier):
            handle = self.driver.current_window_handle
            browser_name = self._get_current_browser()
            session_data = self._load_session_data(browser_name)
            if session_data:
                tags = session_data.get("tags", {})
                if handle not in tags:
                    tags[handle] = []
                if tag not in tags[handle]:
                    tags[handle].append(tag)
                session_data["tags"] = tags
                self._save_session(browser_name, session_data)
                print(f"Tagged tab '{identifier}' with '{tag}'.")
                return True
        return False

    def get_tabs_by_tag(self, tag):
        """Returns handles of tabs that have the given tag."""
        browser_name = self._get_current_browser()
        session_data = self._load_session_data(browser_name)
        if not session_data or "tags" not in session_data:
            return []
        
        handles = []
        all_tags = session_data["tags"]
        available_handles = self.driver.window_handles if self.driver else []
        
        for handle, tags in all_tags.items():
            if tag in tags and handle in available_handles:
                handles.append(handle)
        return handles

    @time_it(logger)
    def list_tabs(self):
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            return []

        tabs = []
        original_window = self.driver.current_window_handle
        
        browser_name = self._get_current_browser()
        session_data = self._load_session_data(browser_name)
        all_tags = session_data.get("tags", {}) if session_data else {}

        try:
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                tabs.append({
                    "id": handle,
                    "title": self.driver.title,
                    "url": self.driver.current_url,
                    "tags": all_tags.get(handle, [])
                })
            # Switch back to the original window
            self.driver.switch_to.window(original_window)
        except WebDriverException as e:
            logger.error(f"Error listing tabs: {e}")
            return []
        
        return tabs

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

    @time_it(logger)
    def start_session(self, browser_name="chrome", headless=False, force=False):
        logger.info(
            f"Starting browser session: {browser_name}",
            extra={"browser": browser_name, "headless": headless, "force": force}
        )
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
            logger.info(
                f"Aria session started for {browser_name}",
                extra={"session_id": self.driver.session_id, "driver_pid": proc.pid, "browser": browser_name}
            )
            
            print(f"Aria session started for {browser_name}")
            return self.driver
        except Exception as e:
            print(f"Error starting {browser_name} session: {e}")
            return None

    def _is_process_running(self, pid):
        """Checks if a process with the given PID is still running."""
        if not pid:
            return True
        if os.name == 'nt':
            import subprocess
            try:
                output = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], capture_output=True, text=True).stdout
                return str(pid) in output
            except:
                return True
        else:
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False

    @time_it(logger)
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
        
        # Optimization: Check if process is still running
        if not self._is_process_running(session_data.get("driver_pid")):
            logger.warning(
                f"Driver process for {browser_name} is no longer running.",
                extra={"browser": browser_name, "driver_pid": session_data.get("driver_pid")}
            )
            session_file = self.get_session_file_path(browser_name)
            if os.path.exists(session_file):
                os.remove(session_file)
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
            logger.info(
                f"Successfully reconnected to {browser_name} session.",
                extra={"browser": browser_name, "session_id": session_data["session_id"]}
            )
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

    @time_it(logger)
    @retry_on_browser_error(retries=2, initial_delay=1)
    def navigate(self, url):
        self.throttle()
        if self.plugin_manager:
            self.plugin_manager.trigger_hook("pre_navigation", url=url)

        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            if self.plugin_manager:
                self.plugin_manager.trigger_hook("post_navigation", url=url, success=False)
            raise SessionError("No active session. Use 'aria open' to start a session.")

        try:
            print(f"Navigating to: {url}")
            logger.info(f"Navigating to URL: {url}", extra={"url": url})
            self.driver.get(url)
            if self.plugin_manager:
                self.plugin_manager.trigger_hook("post_navigation", url=url, success=True)
        except WebDriverException as e:
            if self.plugin_manager:
                self.plugin_manager.trigger_hook("post_navigation", url=url, success=False)
            logger.error(f"WebDriverException during navigation to {url}: {e}", extra={"url": url, "error": str(e)})
            raise NavigationError(f"Failed to navigate to {url}: {e}")
        except Exception as e:
            if self.plugin_manager:
                self.plugin_manager.trigger_hook("post_navigation", url=url, success=False)
            logger.error(f"Unexpected error during navigation to {url}: {e}", extra={"url": url, "error": str(e)})
            raise BrowserError(f"An unexpected error occurred during navigation: {e}")

    def navigate_with_prompt(self, prompt):
        """Uses AI to determine where to navigate based on a prompt."""
        logger.info(f"Navigating with prompt: {prompt}")
        # In a real implementation, this would call Gemini to get a URL or perform a search.
        # For now, we'll just do a search on DuckDuckGo as a heuristic.
        import urllib.parse
        search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(prompt)}"
        self.navigate(search_url)
        print(f"Heuristic: Searching for '{prompt}' on DuckDuckGo.")

    @time_it(logger)
    def goto_tab(self, identifier):
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            print("No active session. Use 'aria open' to start a session.")
            return False

        try:
            handles = self.driver.window_handles
            
            # Normalize identifier
            str_ident = str(identifier)

            # 1. Try by handle (exact match)
            if str_ident in handles:
                self.driver.switch_to.window(str_ident)
                return True

            # 2. Try by index (0-based)
            try:
                idx = int(identifier)
                if 0 <= idx < len(handles):
                    self.driver.switch_to.window(handles[idx])
                    return True
            except (ValueError, TypeError):
                pass
            
            # Store original handle to revert if no match is found
            original_handle = self.driver.current_window_handle

            # 3. Try by partial handle match (if it looks like a handle or is reasonably long)
            if len(str_ident) >= 5:
                for handle in handles:
                    if str_ident in handle:
                        self.driver.switch_to.window(handle)
                        return True

            # 4. Try by title (exact match, case-sensitive)
            for handle in handles:
                self.driver.switch_to.window(handle)
                if self.driver.title == str_ident:
                    return True

            # 5. Try by title (partial, case-insensitive)
            for handle in handles:
                self.driver.switch_to.window(handle)
                if str_ident.lower() in self.driver.title.lower():
                    return True
            
            # 6. Try by URL (partial)
            for handle in handles:
                self.driver.switch_to.window(handle)
                if str_ident in self.driver.current_url:
                    return True

            # If not found, switch back to original window
            self.driver.switch_to.window(original_handle)
            logger.info(f"Tab with identifier '{identifier}' not found.")
            return False
        except WebDriverException as e:
            logger.error(f"Error going to tab: {e}")
            return False

    @time_it(logger)
    @retry_on_browser_error(retries=2, initial_delay=1)
    def get_page_content(self):
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            raise SessionError("No active session. Use 'aria open' to start a session.")

        try:
            return self.driver.find_element(By.TAG_NAME, 'body').text
        except WebDriverException as e:
            logger.error(f"Error getting page content: {e}")
            raise BrowserError(f"Could not retrieve content from the page: {e}")

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
        self.throttle()
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

    def resolve_prompt(self, prompt: str):
        """Parses prompt for tab and tag references and returns (refined_prompt, context)."""
        if not self.driver:
            self.driver = self.connect_to_session()

        # 1. Look for 'tag:NAME'
        tag_matches = re.findall(r'tag:([^\s,;?!\.]+)', prompt, re.IGNORECASE)
        tag_identifiers = []
        for tag in tag_matches:
            tag_identifiers.extend(self.get_tabs_by_tag(tag))

        # 2. Look for 'tab 0', 'tab "My Page"', 'tab google', etc.
        matches = re.findall(r'tab\s+(?:"([^"]+)"|([^\s,;?!\.]+))', prompt, re.IGNORECASE)
        
        # Unique identifiers
        identifiers = list(set(tag_identifiers + [m[0] or m[1] for m in matches]))
        if not identifiers:
            return prompt, ""

        contents = self.get_tabs_content(identifiers)
        
        context_parts = []
        for item in contents:
            context_parts.append(f"--- Content from Tab {item['identifier']} (Title: {item['title']}, URL: {item['url']}) ---\n{item['content']}\n")
        
        context = "\n".join(context_parts)
        return prompt, context
            