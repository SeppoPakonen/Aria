"""
Module to provide enhanced undetected geckodriver functionality for Aria.
This module provides a way to use enhanced undetected geckodriver when needed,
while maintaining compatibility with the main Aria framework.
"""

from undetected_geckodriver import Firefox as UndetectedFirefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile as SeleniumFirefoxProfile


def create_undetected_firefox_session(headless=False, profile_path=None, use_default_profile=False, **kwargs):
    """
    Creates a Firefox session using enhanced undetected geckodriver.

    Args:
        headless (bool): Whether to run in headless mode
        profile_path (str): Path to Firefox profile to use
        use_default_profile (bool): Whether to use the default Firefox profile
        **kwargs: Additional options to pass to Firefox

    Returns:
        WebDriver: An undetected Firefox WebDriver instance
    """
    # Additional options to make the browser less detectable
    if 'options' not in kwargs:
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        kwargs['options'] = options
    else:
        if headless:
            kwargs['options'].add_argument("--headless")

    # Apply any additional options from kwargs
    for key, value in kwargs.items():
        if hasattr(kwargs.get('options', None), key) and key != 'options':
            setattr(kwargs['options'], key, value)

    # Create the undetected Firefox instance with profile support
    driver = UndetectedFirefox(
        options=kwargs.get('options'),
        service=kwargs.get('service'),
        keep_alive=kwargs.get('keep_alive', True),
        use_default_profile=use_default_profile,
        profile_path=profile_path
    )

    return driver


def get_undetected_firefox_example():
    """
    Provides an example of how to use undetected geckodriver as requested.
    """
    driver = create_undetected_firefox_session()
    return driver


def get_undetected_firefox_with_default_profile():
    """
    Creates an undetected Firefox instance using the default Firefox profile.
    """
    driver = create_undetected_firefox_session(use_default_profile=True)
    return driver


# For direct import compatibility with the requested usage
Firefox = UndetectedFirefox
Options = FirefoxOptions
Profile = SeleniumFirefoxProfile