"""
Wrapper module for undetected geckodriver to replace regular geckodriver.
This module provides a Firefox class that behaves like selenium's Firefox
but uses undetected geckodriver to avoid bot detection.
"""

from undetected_geckodriver import Firefox as UndetectedFirefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile as SeleniumFirefoxProfile
from selenium.webdriver.remote.webdriver import WebDriver


def create_undetected_firefox(options=None, profile=None, headless=False, **kwargs):
    """
    Creates a Firefox instance using undetected geckodriver.

    Args:
        options: Firefox options to use
        profile: Firefox profile to use
        headless: Whether to run in headless mode
        **kwargs: Additional arguments to pass to the Firefox constructor

    Returns:
        WebDriver: A Firefox WebDriver instance that's harder to detect as automated
    """
    if options is None:
        options = FirefoxOptions()

    if headless:
        options.add_argument("--headless")

    if profile:
        if isinstance(profile, str):
            # If profile is a string path, create a FirefoxProfile object from selenium
            options.profile = SeleniumFirefoxProfile(profile)
        else:
            options.profile = profile

    # Additional options to make the browser less detectable
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("media.volume_scale", "0.0")

    # Pass any additional options from kwargs
    for key, value in kwargs.items():
        if hasattr(options, key):
            setattr(options, key, value)

    # Create the undetected Firefox instance
    driver = UndetectedFirefox(options=options)

    return driver


class FirefoxWrapper:
    """
    A wrapper class that provides the same interface as selenium's Firefox
    but uses undetected geckodriver internally.
    """

    def __init__(self, options=None, profile=None, headless=False, **kwargs):
        self.driver = create_undetected_firefox(
            options=options,
            profile=profile,
            headless=headless,
            **kwargs
        )

    def __getattr__(self, name):
        """
        Delegate attribute access to the underlying driver instance.
        This allows the wrapper to behave like a regular WebDriver.
        """
        return getattr(self.driver, name)

    def quit(self):
        """Quit the browser and clean up resources."""
        if hasattr(self.driver, 'quit'):
            self.driver.quit()

    def close(self):
        """Close the current window."""
        if hasattr(self.driver, 'close'):
            self.driver.close()


# For backward compatibility and easy replacement
Firefox = UndetectedFirefox
Options = FirefoxOptions
Profile = SeleniumFirefoxProfile