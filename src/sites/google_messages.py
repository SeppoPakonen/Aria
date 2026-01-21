import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from navigator import AriaNavigator

logger = logging.getLogger("aria.sites.google_messages")

class GoogleMessagesScraper:
    """Scraper for Google Messages Web."""
    URL = "https://messages.google.com/web/conversations"

    def __init__(self, navigator: AriaNavigator, site_manager):
        self.navigator = navigator
        self.sm = site_manager
        self.site_name = "google-messages"

    def navigate(self):
        """Navigates to the Google Messages web interface."""
        print(f"Navigating to {self.URL}...")
        self.navigator.navigate(self.URL)
        
        # Wait for the main conversation list to appear
        try:
            print("Waiting for Google Messages to load (ensure you are paired)...")
            # Look for a common element in the conversation list
            self.navigator.wait_for_element("mws-conversations-list", by=By.TAG_NAME, timeout=30)
            print("Google Messages loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load Google Messages: {e}")
            print("Error: Google Messages did not load within 30 seconds. Please check pairing.")
            return False

    def refresh(self, deep=False):
        """Orchestrates the Google Messages data refresh."""
        if not self.navigate():
            return False
        
        print("Starting data refresh for Google Messages...")

    def scrape_all_conversations(self):
        """Iterates through all conversations and scrapes their content."""
        # 1. Get initial list of conversation elements
        items = self.navigator.driver.find_elements(By.CSS_SELECTOR, "mws-conversation-list-item")
        print(f"Found {len(items)} conversation threads.")
        
        all_data = []
        
        for i in range(len(items)):
            # Re-fetch items to avoid stale element exceptions
            items = self.navigator.driver.find_elements(By.CSS_SELECTOR, "mws-conversation-list-item")
            if i >= len(items): break
            
            item = items[i]
            try:
                # Get conversation name
                name = item.find_element(By.CSS_SELECTOR, "[data-e2e-conversation-name]").text.strip()
                print(f"Scraping conversation: {name}")
                
                # Click the internal 'a' link via JS to ensure thread loads
                link = item.find_element(By.TAG_NAME, "a")
                self.navigator.driver.execute_script("arguments[0].click();", link)
                time.sleep(3) # Wait for messages to load
                
                # Extract messages
                messages = self.extract_visible_messages()
                
                convo_data = {
                    "name": name,
                    "id": i,
                    "scraped_at": time.ctime(),
                    "messages": messages
                }
                
                # Save individual conversation file
                safe_name = "".join([c if c.isalnum() else "_" for c in name])
                self.sm.save_data(self.site_name, f"convo_{safe_name}.json", convo_data)
                
                all_data.append({"name": name, "message_count": len(messages)})
            except Exception as e:
                logger.error(f"Error scraping conversation {i}: {e}")
        
        # Save the master list
        self.sm.save_data(self.site_name, "conversations.json", all_data)
        return all_data

    def extract_visible_messages(self):
        """Extracts messages from the currently open conversation thread using confirmed tags."""
        from bs4 import BeautifulSoup
        messages = []
        try:
            # Get the page source
            soup = BeautifulSoup(self.navigator.driver.page_source, 'html.parser')
            
            # Find message wrappers
            msg_wrappers = soup.find_all("mws-message-wrapper")
            
            for wrapper in msg_wrappers:
                try:
                    # Identify sender
                    classes = wrapper.get("class", [])
                    is_outgoing = "outgoing" in classes
                    
                    # 1. Extract Text from mws-text-message-part
                    text_el = wrapper.select_one("mws-text-message-part")
                    text = text_el.get_text(strip=True) if text_el else ""
                    
                    # 2. Extract Media
                    media_info = []
                    img_els = wrapper.select("img")
                    for img in img_els:
                        src = img.get("src")
                        if src and not src.startswith("data:"):
                            media_info.append({"type": "image", "url": src})
                    
                    # 3. Extract Timestamp from aria-label
                    timestamp = "Unknown"
                    if text_el and text_el.has_attr("aria-label"):
                        label = text_el["aria-label"]
                        # Look for time pattern HH.MM or HH:MM
                        import re
                        # Typical labels: "Sinä sanoit: ... Lähetetty 20. tammikuuta 2026 klo 16.33"
                        # Or "Contact sanoi: ... Lähetetty 16.33"
                        match = re.search(r"(\d{1,2}[\.:]\d{2})", label)
                        if match:
                            timestamp = match.group(1)
                        else:
                            # Try finding it in relative timestamp as fallback
                            ts_el = wrapper.select_one("mws-relative-timestamp")
                            if ts_el:
                                timestamp = ts_el.get_text(strip=True)
                    
                    if text or media_info:
                        messages.append({
                            "text": text,
                            "timestamp": timestamp,
                            "type": "sent" if is_outgoing else "received",
                            "media": media_info
                        })
                except Exception as e:
                    continue
        except Exception as e:
            logger.error(f"Error extracting messages: {e}")
            
        return messages

    def extract_media(self, msg_el):
        """Detects and downloads media from a message element."""
        media_list = []
        
        # Check for images
        try:
            images = msg_el.find_elements(By.CSS_SELECTOR, "img.content")
            for img in images:
                src = img.get_attribute("src")
                if src:
                    local_path = self.download_file(src, "image")
                    if local_path:
                        media_list.append({"type": "image", "path": local_path, "url": src})
        except:
            pass

        # Check for videos/audio (often represented as specific tags or download links in Google Messages)
        try:
            # Google Messages often uses <video> or <a> with specific classes for attachments
            videos = msg_el.find_elements(By.CSS_SELECTOR, "video")
            for video in videos:
                src = video.get_attribute("src")
                if src:
                    local_path = self.download_file(src, "video")
                    if local_path:
                        media_list.append({"type": "video", "path": local_path, "url": src})
        except:
            pass

        return media_list

    def download_file(self, url, category):
        """Downloads a file to the local media directory."""
        if not url or url.startswith("blob:"):
            # blob URLs require different handling (e.g., executing JS to get base64)
            # For now, we skip blobs or handle them as placeholders
            return None

        import requests
        import hashlib
        
        try:
            # Create a unique filename based on URL hash
            ext = ".bin"
            if "image" in category: ext = ".png"
            elif "video" in category: ext = ".mp4"
            
            name_hash = hashlib.md5(url.encode()).hexdigest()
            filename = f"{category}_{name_hash}{ext}"
            
            site_dir = self.sm.get_site_dir(self.site_name)
            local_path = os.path.join(site_dir, "media", filename)
            
            if os.path.exists(local_path):
                return f"media/{filename}"

            # We use requests if possible, but for authenticated sessions, 
            # we might need to use the browser's cookies.
            # Simplified approach:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(response.content)
                return f"media/{filename}"
        except Exception as e:
            logger.error(f"Failed to download media {url}: {e}")
        
        return None
