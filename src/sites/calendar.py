import time
import logging
import re
import os
import json
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from navigator import AriaNavigator

logger = logging.getLogger("aria.sites.calendar")

class CalendarScraper:
    """Scraper for Google Calendar."""
    URL = "https://calendar.google.com/calendar/u/0/r"

    def __init__(self, navigator: AriaNavigator, site_manager):
        self.navigator = navigator
        self.sm = site_manager
        self.site_name = "calendar"

    def navigate(self):
        """Navigates to Google Calendar and waits for load."""
        curr_url = self.navigator.driver.current_url
        if "calendar.google.com/calendar" in curr_url:
            # Check if we're actually in the app
            try:
                self.navigator.wait_for_element('div[role="main"]', by=By.CSS_SELECTOR, timeout=5)
                return True
            except:
                pass

        print(f"Navigating to {self.URL}...")
        self.navigator.navigate(self.URL)
        
        try:
            print("Waiting for Google Calendar to load...")
            # Look for the calendar grid or main container
            self.navigator.wait_for_element('div[role="main"], div[role="grid"], [aria-label*="Kalenteri"]', by=By.CSS_SELECTOR, timeout=45)
            time.sleep(5)
            
            # Check for login redirection
            if "accounts.google.com" in self.navigator.driver.current_url:
                print("Error: Redirected to Google Login. Please log in manually in the browser first.")
                return False

            print("Google Calendar loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load Calendar: {e}")
            # Check for Sign In button (Kirjaudu sisään)
            try:
                html = self.navigator.driver.page_source.lower()
                if "kirjaudu sisään" in html or "sign in" in html:
                    print("Error: Google Calendar is not logged in.")
                else:
                    print(f"Error: Calendar did not load correctly. Title: {self.navigator.driver.title}")
            except:
                pass
            return False

    def refresh(self, deep=False):
        """Orchestrates the Google Calendar data refresh."""
        if not self.navigate():
            return False
        
        print("Starting data refresh for Google Calendar...")
        events = self.scrape_events()
        print(f"Found {len(events)} events in current view.")
        
        self.sm.save_data(self.site_name, "events.json", events)
        self.sm.save_data(self.site_name, "metadata.json", {
            "last_refresh": time.ctime(),
            "event_count": len(events)
        })
        return True

    def scrape_events(self):
        """Extracts events from the current calendar view."""
        try:
            # Use BeautifulSoup for fast extraction of the main container
            main_html = self.navigator.driver.execute_script("""
                const main = document.querySelector('div[role="main"]') || 
                             document.querySelector('div[role="grid"]') ||
                             document.body;
                return main.innerHTML;
            """)
            soup = BeautifulSoup(main_html, 'html.parser')
            
            events = []
            # In Finnish Google Calendar, event details might be in various elements.
            # We'll look for strings that look like "Time - Time, Event Title"
            # or aria-labels that contain event summaries.
            
            # 1. Check all elements with aria-label
            all_elements = soup.select('[aria-label]')
            for el in all_elements:
                label = el.get('aria-label', '')
                if len(label) > 10 and "," in label:
                    # Check for Finnish time pattern: "9.00–10.00"
                    if re.search(r"\d{1,2}[\.:]\d{2}", label):
                        events.append({
                            "summary": label,
                            "raw_label": label
                        })
            
            # 2. Heuristic: search for elements with title-like and time-like text
            # if no labeled events found.
            if not events:
                text_content = self.navigator.driver.execute_script("return document.body.innerText")
                # Look for lines that look like events: "9.00–10.00, My Event"
                lines = text_content.split('\n')
                for line in lines:
                    if re.search(r"\d{1,2}[\.:]\d{2}", line) and len(line) > 10:
                        events.append({
                            "summary": line,
                            "raw_label": line
                        })

            # Deduplicate by label
            seen = set()
            unique_events = []
            for e in events:
                if e['raw_label'] not in seen:
                    unique_events.append(e)
                    seen.add(e['raw_label'])
                    
            return unique_events
        except Exception as e:
            logger.error(f"Error scraping Calendar events: {e}")
            return []
