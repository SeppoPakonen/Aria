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

    def refresh(self, deep=False):
        """Orchestrates the Threads data refresh. Default is shallow (feed only)."""
        if not self.navigate():
            return False
        
        print(f"Starting {'deep' if deep else 'shallow'} data refresh for Threads...")
        
        profile_url = None
        if deep:
            # 1. Discover Profile URL and crawl everything
            profile_url = self.discover_profile_url()
            if not profile_url:
                print("  Warning: Could not discover personal profile URL.")
            else:
                print(f"  Discovered profile: {profile_url}")
                self.scrape_personal_content(profile_url)
        else:
            print("  Skipping personal profile crawl (shallow mode).")

        # 2. General Feed
        posts = self.scrape_feed()
        print(f"Found {len(posts)} unique posts in general feed.")
        self.sm.save_data(self.site_name, "feed.json", posts)
        
        self.sm.save_data(self.site_name, "metadata.json", {
            "last_refresh": time.ctime(),
            "profile_url": profile_url or self.discover_profile_url(),
            "mode": "deep" if deep else "shallow"
        })
        return True

    def discover_profile_url(self):
        """Finds the personal profile URL from the navigation bar."""
        script = """
        const links = Array.from(document.querySelectorAll('a[href^="/@"]'));
        // Usually the profile link is the last one in the nav or has a specific avatar/icon
        const profileLink = links.find(a => a.querySelector('svg[aria-label*="Profiili"]') || a.querySelector('svg[aria-label*="Profile"]'));
        return profileLink ? 'https://www.threads.net' + profileLink.getAttribute('href') : null;
        """
        return self.navigator.driver.execute_script(script)

    def scrape_personal_content(self, profile_url):
        """Scrapes the user's own posts and replies."""
        print(f"  Scraping personal profile: {profile_url}")
        self.navigator.navigate(profile_url)
        time.sleep(5)
        
        # 1. Get thread links from "Threads" tab
        post_links = self.discover_thread_links()
        print(f"    Found {len(post_links)} personal threads.")
        
        # 2. Switch to "Replies" tab
        self.switch_to_replies_tab()
        time.sleep(4)
        reply_links = self.discover_thread_links()
        print(f"    Found {len(reply_links)} threads with replies.")
        
        # Combine and deduplicate links
        all_links = list(set(post_links + reply_links))
        
        # Update registry with thread names/IDs
        thread_names = []
        
        # 3. Scrape each thread fully
        for i, link in enumerate(all_links):
            print(f"    Scraping full thread {i+1}/{len(all_links)}: {link}")
            res = self.scrape_full_thread(link)
            if res:
                thread_names.append(res) # Return the thread title/identifier

        # Update persistent registry so they show up in 'list'
        if thread_names:
            self.sm.update_registry(self.site_name, thread_names)

    def discover_thread_links(self):
        """Finds links to full threads on the current profile page."""
        script = """
        return Array.from(document.querySelectorAll('a[href*="/post/"]'))
            .map(a => 'https://www.threads.net' + a.getAttribute('href'));
        """
        return self.navigator.driver.execute_script(script)

    def switch_to_replies_tab(self):
        """Clicks the 'Replies' (Vastaukset) tab on the profile."""
        script = """
        const spans = Array.from(document.querySelectorAll('span'));
        const tab = spans.find(s => s.innerText.includes('Vastaukset') || s.innerText.includes('Replies'));
        if (tab) {
            tab.click();
            return true;
        }
        return false;
        """
        self.navigator.driver.execute_script(script)

    def scrape_full_thread(self, thread_url):
        """Navigates to a thread and scrapes all messages/replies with scrolling."""
        # Clean URL to get a stable ID
        parts = thread_url.split('/post/')
        if len(parts) < 2: return None
        
        post_id_part = parts[1].split('?')[0].split('/')[0]
        
        self.navigator.navigate(thread_url)
        time.sleep(5)
        
        # Scroll to load all replies
        last_height = self.navigator.driver.execute_script("return document.body.scrollHeight")
        for _ in range(5): # Limit scrolling to avoid infinite loops
            self.navigator.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.navigator.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Scrape all posts in the thread
        messages = self.scrape_feed()
        
        if messages:
            # For threads where we replied to someone, the first message might be them.
            # We'll use the URL and the user of the first message for the registry.
            first = messages[0]
            # Include ID in name to ensure uniqueness in registry
            thread_display_name = f"Thread {post_id_part} by {first['user']}: {first['text'][:30]}..."
            
            filename = f"thread_{post_id_part}.json"
            self.sm.save_data(self.site_name, filename, {
                "url": thread_url,
                "id": post_id_part,
                "display_name": thread_display_name,
                "scraped_at": time.ctime(),
                "messages": messages
            })
            return thread_display_name
        return None

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
            author_links = soup.select('a[href^="/@"]')
            
            for link in author_links:
                try:
                    # Filter out post links, but keep profile links for authorship
                    href = link.get('href', '')
                    is_post_link = '/post/' in href
                    
                    # 1. Extract Username
                    user = link.get_text(strip=True)
                    if not user:
                        img = link.select_one('img')
                        if img and img.has_attr('alt'):
                            match = re.search(r"Käyttäjän\s+(\S+)\s+", img['alt'])
                            if match:
                                user = match.group(1)
                    
                    if not user or user == "Etusivu": continue
                    
                    # Filter out usernames that look like timestamps (e.g. "3 pv", "4.1.2026")
                    if re.match(r"^\d+[\s\.].*", user):
                        continue
                    
                    # 2. Find the post container
                    # Search for role="article" or a common wrapper
                    container = link.find_parent('div', role='article') or \
                                link.find_parent('div', class_=lambda c: c and 'x1a2a7pz' in c) or \
                                link.parent.parent.parent
                    
                    if not container: continue
                    
                    # 3. Extract Text
                    # Look for the content block (dir="auto")
                    text = ""
                    text_els = container.select('div[dir="auto"], span[dir="auto"]')
                    # We look for the longest text block that isn't the username
                    candidates = []
                    for tel in text_els:
                        t = tel.get_text(strip=True)
                        if t and t != user and not t.endswith('sitten') and not t.endswith('min') and len(t) > 2:
                            candidates.append(t)
                    
                    if candidates:
                        # Pick the one that's likely the body (usually the longest or first significant)
                        text = max(candidates, key=len)
                    
                    # 4. Extract Timestamp
                    ts = "Unknown"
                    ts_el = container.select_one('time')
                    if ts_el:
                        ts = ts_el.get_text(strip=True)
                    elif is_post_link:
                        ts = link.get_text(strip=True)
                    
                    # 5. Extract Likes (Engagement)
                    likes = 0
                    # Look for links/spans containing "tykkäystä" or "likes"
                    # Threads often hides this in a very specific sub-element
                    like_els = container.select('a, span, div')
                    for le in like_els:
                        lt = le.get_text(strip=True).lower()
                        # Match: "5 tykkäystä", "12 likes", "1 tykkää", etc.
                        match = re.search(r"(\d+)\s+(tykkä|like)", lt)
                        if match:
                            likes = int(match.group(1))
                            break
                        # Handle "1 tykkää" / "1 like" without plural
                        elif lt == "1 tykkää" or lt == "1 like":
                            likes = 1
                            break

                    if user and text:
                        posts.append({
                            "user": user,
                            "text": text,
                            "timestamp": ts,
                            "likes": likes
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