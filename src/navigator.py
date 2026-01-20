import os
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, StaleElementReferenceException

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
from utils import retry
import time
from selenium.common.exceptions import WebDriverException

logger = get_logger("navigator")

class BaseNavigator:
    """Abstract base class for all navigators."""
    def __init__(self):
        self.plugin_manager = None

    def start_session(self, browser_name="chrome", headless=False, force=False, profile=None):
        raise NotImplementedError()

    def connect_to_session(self, browser_name=None):
        raise NotImplementedError()

    def close_session(self, browser_name=None):
        raise NotImplementedError()

    def navigate(self, url):
        raise NotImplementedError()

    def navigate_with_prompt(self, prompt):
        raise NotImplementedError()

    def list_tabs(self):
        raise NotImplementedError()

    def goto_tab(self, identifier):
        raise NotImplementedError()

    def get_page_content(self):
        raise NotImplementedError()

    def new_tab(self, url="about:blank"):
        raise NotImplementedError()

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

class AriaNavigator(BaseNavigator):
    def __init__(self):
        super().__init__()
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

    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Waits for an element to be present and visible in the DOM."""
        if not self.driver:
            self.driver = self.connect_to_session()
        if not self.driver:
            raise SessionError("No active session.")
            
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located((by, selector)))
            return element
        except TimeoutException:
            logger.error(f"Timed out waiting for element: {selector}")
            raise BrowserError(f"Timed out waiting for element: {selector}")

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
    def start_session(self, browser_name="chrome", headless=False, force=False, profile=None):
        logger.info(
            f"Starting browser session: {browser_name}",
            extra={"browser": browser_name, "headless": headless, "force": force, "profile": profile}
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
                if os.path.exists(session_file):
                    os.remove(session_file)

        try:
            import subprocess
            import time
            import socket
            import configparser

            def find_free_port():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', 0))
                    return s.getsockname()[1]

            port = find_free_port()
            
            driver_path = None
            options = None
            
            def get_binary_path(browser_type):
                if browser_type == "chrome":
                    paths = [
                        "/usr/bin/google-chrome",
                        "/usr/bin/google-chrome-stable",
                        "/usr/bin/chromium",
                        "/usr/bin/chromium-browser",
                        "/snap/bin/chromium",
                        "/snap/bin/chromium-browser"
                    ]
                elif browser_type == "firefox":
                    paths = [
                        "/usr/bin/firefox",
                        "/usr/bin/firefox-esr",
                        "/snap/bin/firefox",
                        "/usr/local/bin/firefox"
                    ]
                else:
                    return None
                    
                for path in paths:
                    if os.path.exists(path):
                        return path
                return None

            def get_firefox_profile_path(profile_name_or_path):
                if not profile_name_or_path:
                    return None
                
                # If it looks like a path, use it
                if os.path.isabs(profile_name_or_path) or os.path.exists(profile_name_or_path):
                    return profile_name_or_path
                
                # Check profiles.ini
                profiles_ini_path = os.path.join(os.path.expanduser("~"), ".mozilla", "firefox", "profiles.ini")
                if os.path.exists(profiles_ini_path):
                    try:
                        config = configparser.ConfigParser()
                        config.read(profiles_ini_path)
                        for section in config.sections():
                            if section.startswith("Profile"):
                                name = config.get(section, "Name", fallback="")
                                if name == profile_name_or_path:
                                    path = config.get(section, "Path", fallback="")
                                    is_relative = config.getint(section, "IsRelative", fallback=1)
                                    if is_relative:
                                        return os.path.join(os.path.dirname(profiles_ini_path), path)
                                    return path
                    except Exception as e:
                        logger.error(f"Error parsing profiles.ini: {e}")
                
                return None

            if browser_name == "chrome":
                driver_path = ChromeDriverManager().install()
                options = ChromeOptions()
                if os.name == 'posix':
                    bin_path = get_binary_path("chrome")
                    if bin_path:
                        logger.info(f"Found Chrome/Chromium binary at: {bin_path}")
                        options.binary_location = bin_path
            elif browser_name == "firefox":
                driver_path = GeckoDriverManager().install()
                options = FirefoxOptions()
                if os.name == 'posix':
                    bin_path = get_binary_path("firefox")
                    if bin_path:
                        logger.info(f"Found Firefox binary at: {bin_path}")
                        options.binary_location = bin_path
                
                if profile:
                    profile_path = get_firefox_profile_path(profile)
                    if profile_path:
                        print(f"Using Firefox profile (Direct): {profile_path}")
                        # Use the profile directly (requires Firefox to be closed)
                        options.add_argument("-profile")
                        options.add_argument(profile_path)
                    else:
                        print(f"Warning: Could not find Firefox profile '{profile}'. Using default.")

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
        driver_pid = session_data.get("driver_pid")
        if not self._is_process_running(driver_pid):
            logger.warning(
                f"Driver process for {browser_name} (PID {driver_pid}) is no longer running.",
                extra={"browser": browser_name, "driver_pid": driver_pid}
            )
            self._remove_session_file(browser_name)
            return None

        try:
            if browser_name == "chrome":
                options = ChromeOptions()
            elif browser_name == "firefox":
                options = FirefoxOptions()
            elif browser_name == "edge":
                options = EdgeOptions()
            else:
                # Default to ChromeOptions if unknown, or return None
                options = ChromeOptions()

            driver = ReusableRemote(
                command_executor=session_data["url"],
                options=options,
                session_id=session_data["session_id"]
            )
            
            # Verify it works with a timeout
            driver.set_page_load_timeout(5)
            driver.set_script_timeout(5)
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
            # If we failed to connect but the process is still "running", it might be a zombie
            self.close_session(browser_name)
            return None

    def _remove_session_file(self, browser_name):
        session_file = self.get_session_file_path(browser_name)
        if os.path.exists(session_file):
            os.remove(session_file)
        if self._get_current_browser() == browser_name:
            current_file = self.get_session_file_path()
            if os.path.exists(current_file):
                os.remove(current_file)

    def cleanup_orphaned_sessions(self):
        """Identifies and cleans up stale session files and orphaned driver processes."""
        logger.info("Starting cleanup of orphaned sessions.")
        browsers = self.list_active_browsers()
        cleaned_count = 0
        
        for browser in browsers:
            session_data = self._load_session_data(browser)
            if not session_data:
                continue
                
            is_healthy = False
            try:
                # Try to connect and check health
                if browser == "chrome":
                    options = ChromeOptions()
                elif browser == "firefox":
                    options = FirefoxOptions()
                elif browser == "edge":
                    options = EdgeOptions()
                else:
                    options = ChromeOptions()

                # Short timeout for cleanup check
                driver = ReusableRemote(
                    command_executor=session_data["url"],
                    options=options,
                    session_id=session_data["session_id"]
                )
                _ = driver.current_url
                is_healthy = True
                driver.quit() # Close the connection but the session might persist if not ReusableRemote
            except:
                is_healthy = False
            
            if not is_healthy:
                logger.info(f"Cleaning up unhealthy session for {browser}")
                self.close_session(browser)
                cleaned_count += 1
        
        return cleaned_count

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
                else:
                    options = ChromeOptions()
                
                driver = ReusableRemote(
                    command_executor=session_data["url"],
                    options=options,
                    session_id=session_data["session_id"]
                )
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
                        os.kill(driver_pid, signal.SIGKILL) # More aggressive cleanup
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
    @retry((WebDriverException, BrowserError), tries=3, delay=1)
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

    def extract_links(self):
        """Extracts visible links from the current page."""
        if not self.driver:
            return []
        
        elements = self.driver.find_elements(By.TAG_NAME, "a")
        links = []
        for i, el in enumerate(elements):
            try:
                if el.is_displayed():
                    text = el.text.strip() or el.get_attribute("aria-label") or ""
                    href = el.get_attribute("href")
                    if href and (text or href):
                        links.append({"id": i, "text": text[:50], "url": href})
            except:
                pass
        return links[:100] # Limit to 100 links to save context

    def navigate_with_prompt(self, prompt):
        """Uses AI to determine where to navigate based on a prompt."""
        logger.info(f"Navigating with prompt: {prompt}")
        
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            print("No active session. Use 'aria open' to start a session.")
            return

        # 1. Get current context (links)
        links = self.extract_links()
        
        # 2. Get AI Provider
        provider = None
        if self.plugin_manager:
            # Try to get default 'gemini' or any available
            provider = self.plugin_manager.get_ai_provider("gemini")
            if not provider:
                providers = self.plugin_manager.list_ai_providers()
                if providers:
                    provider = self.plugin_manager.get_ai_provider(providers[0])
        
        url_to_navigate = None
        
        if provider and links:
            import json
            context_str = json.dumps(links, indent=2)
            
            ai_prompt = (
                f"User request: '{prompt}'\n\n"
                f"Current Page Links:\n{context_str}\n\n"
                "Determine the best action.\n"
                "If the user wants to click a specific link or navigate to a page mentioned above, return ONLY a JSON object: {\"url\": \"THE_URL\"}.\n"
                "If the user wants to search the web or the request cannot be fulfilled by the links above, return ONLY: {\"search\": \"SEARCH_QUERY\"}.\n"
                "Return ONLY valid JSON."
            )
            
            try:
                print("Analyzing page content with AI...")
                response = provider.generate(ai_prompt, output_format="json")
                # Clean up response if needed (markdown stripping is handled in provider usually, but be safe)
                if response.startswith("```"):
                    response = response.split("\n", 1)[1].rsplit("\n", 1)[0]
                
                data = json.loads(response)
                if "url" in data:
                    url_to_navigate = data["url"]
                    print(f"AI identified target: {url_to_navigate}")
                elif "search" in data:
                    print(f"AI suggests searching for: {data['search']}")
                    prompt = data['search'] # Fallthrough to search logic
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                print(f"AI analysis failed: {e}")

        if url_to_navigate:
            self.navigate(url_to_navigate)
            return

        # Fallback to DuckDuckGo search
        import urllib.parse
        search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(prompt)}"
        self.navigate(search_url)
        print(f"Searching for '{prompt}' on DuckDuckGo.")

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
    @retry((WebDriverException, BrowserError, StaleElementReferenceException), tries=3, delay=1)
    def get_page_content(self):
        if not self.driver:
            self.driver = self.connect_to_session()
        
        if not self.driver:
            raise SessionError("No active session. Use 'aria open' to start a session.")

        try:
            # Wait for body to be present
            body = self.wait_for_element('body', by=By.TAG_NAME, timeout=5)
            return body.text
        except (WebDriverException, BrowserError) as e:
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
            