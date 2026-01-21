import time
import logging
import re
import os
import json
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from navigator import AriaNavigator

logger = logging.getLogger("aria.sites.threads")

class ThreadsScraper:
    """Scraper for Threads.net."""
    URL = "https://www.threads.net/"

    def __init__(self, navigator: AriaNavigator, site_manager):
        self.navigator = navigator
        self.sm = site_manager
        self.site_name = "threads"

    def navigate(self):
        """Navigates to Threads and waits for full load."""
        if "/threads.net" in self.navigator.driver.current_url or "/threads.com" in self.navigator.driver.current_url:
            # Check if we are actually in the app vs landing page
            try:
                self.navigator.wait_for_element("svg[aria-label='Threads']", by=By.CSS_SELECTOR, timeout=5)
                return True
            except:
                pass

        print(f"Navigating to {self.URL}...")
        self.navigator.navigate(self.URL)
        
        try:
            print("Waiting for Threads to fully load...")
            # Wait for either the Threads logo or the navigation bar
            self.navigator.wait_for_element("svg[aria-label='Threads'], nav, a[href='/']", by=By.CSS_SELECTOR, timeout=45)
            time.sleep(5)
            print("Threads loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load Threads: {e}")
            print("Error: Threads did not load. Please ensure you are logged in.")
            return False

    def refresh(self):
        """Orchestrates the Threads data refresh."""
        if not self.navigate():
            return False
        
        print("Starting data refresh for Threads...")
        posts = self.scrape_feed()
        print(f"Found {len(posts)} unique posts in feed.")
        
        self.sm.save_data(self.site_name, "feed.json", posts)
        self.sm.save_data(self.site_name, "metadata.json", {
            "last_refresh": time.ctime(),
            "post_count": len(posts)
        })
        return True

    def scrape_feed(self):
        """Extracts posts from the current feed using a robust anchor-first strategy."""
        from bs4 import BeautifulSoup
        try:
            # Capture the entire scroller content
            main_html = self.navigator.driver.execute_script("""
                const main = document.querySelector('div[role="main"]') || 
                             document.querySelector('div[aria-label*="teksti"]') ||
                             document.body;
                return main.innerHTML;
            """)
            soup = BeautifulSoup(main_html, 'html.parser')
            
            posts = []
            
            # Find all profile links
            author_links = soup.select('a[href^="/@"]:not([href*="/post/"])')
            
            for link in author_links:
                try:
                    # 1. Extract Username
                    # If link text is empty, try to find an image alt or a nested span
                    user = link.get_text(strip=True)
                    if not user:
                        img = link.select_one('img')
                        if img and img.has_attr('alt'):
                            # Alt usually: "Käyttäjän username profiilikuva"
                            match = re.search(r"Käyttäjän\s+(\S+)\s+", img['alt'])
                            if match:
                                user = match.group(1)
                    
                    if not user or user == "Etusivu": continue
                    
                    # 2. Find the post container
                    # We walk up to a common wrapper like x1a2a7pz
                    container = None
                    curr = link
                    for _ in range(10):
                        if curr.name == 'div' and curr.has_attr('class') and 'x1a2a7pz' in str(curr.get('class')):
                            container = curr
                            break
                        if not curr.parent: break
                        curr = curr.parent
                    
                    if not container:
                        # Fallback to grandparent if x1a2a7pz not found
                        container = link.parent.parent.parent
                    
                    # 3. Extract Text
                    text = ""
                    text_els = container.select('div[dir="auto"], span[dir="auto"]')
                    for tel in text_els:
                        t = tel.get_text(strip=True)
                        if t and t != user and not t.endswith('sitten') and len(t) > 10:
                            text = t
                            break
                    
                    # 4. Extract Timestamp
                    ts = "Unknown"
                    ts_el = container.select_one('time')
                    if ts_el:
                        ts = ts_el.get_text(strip=True)
                    
                    if user and text:
                        posts.append({
                            "user": user,
                            "text": text,
                            "timestamp": ts
                        })
                except:
                    continue
            
            # Deduplicate
            seen = set()
            unique_posts = []
            for p in posts:
                key = f"{p['user']}:{p['text'][:100]}"
                if key not in seen:
                    unique_posts.append(p)
                    seen.add(key)
                    
            return unique_posts
        except Exception as e:
            logger.error(f"Error scraping Threads feed: {e}")
            return []

    def safe_fn(self, name):
        return "".join([c if c.isalnum() else "_" for c in name])