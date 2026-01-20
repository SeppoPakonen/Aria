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

    def refresh(self):
        """Orchestrates the full data refresh/scraping process."""
        # Note: Navigation is now handled by aria.py before calling refresh
        # but we check if we are on the right page.
        if self.URL not in self.navigator.driver.current_url:
            if not self.navigate():
                return False
        
        print("Starting data refresh for Google Messages...")
        conversations = self.scrape_all_conversations()
        
        # Save a metadata summary
        self.sm.save_data(self.site_name, "metadata.json", {
            "last_refresh": time.ctime(),
            "conversation_count": len(conversations)
        })
        return True

    def scrape_all_conversations(self):
        """Iterates through all conversations and scrapes their content."""
        # 1. Get initial list of conversation elements
        # We use a broader selector for the conversation items
        items = self.navigator.driver.find_elements(By.CSS_SELECTOR, "mws-conversation-list-item")
        print(f"Found {len(items)} conversation threads.")
        
        all_data = []
        
        for i in range(len(items)):
            # Re-fetch items to avoid stale element exceptions
            items = self.navigator.driver.find_elements(By.CSS_SELECTOR, "mws-conversation-list-item")
            if i >= len(items): break
            
            item = items[i]
            try:
                # Get conversation name/title
                name = item.find_element(By.CSS_SELECTOR, ".name-container").text.strip()
                print(f"Scraping conversation: {name}")
                
                # Click the conversation to load messages
                item.click()
                time.sleep(2) # Wait for messages to load
                
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
        """Extracts messages from the currently open conversation thread."""
        messages = []
        try:
            # Look for message elements
            msg_elements = self.navigator.driver.find_elements(By.CSS_SELECTOR, "mws-message-wrapper")
            for msg_el in msg_elements:
                try:
                    # Identify sender
                    is_outgoing = "outgoing" in msg_el.get_attribute("class")
                    
                    # 1. Extract Text
                    text = ""
                    try:
                        text = msg_el.find_element(By.CSS_SELECTOR, ".text-msg").text.strip()
                    except:
                        pass
                    
                    # 2. Extract Media
                    media_info = self.extract_media(msg_el)
                    
                    # 3. Extract Timestamp
                    try:
                        timestamp = msg_el.find_element(By.CSS_SELECTOR, ".timestamp").text.strip()
                    except:
                        timestamp = "Unknown"
                    
                    msg_data = {
                        "text": text,
                        "timestamp": timestamp,
                        "type": "sent" if is_outgoing else "received"
                    }
                    
                    if media_info:
                        msg_data["media"] = media_info
                    
                    if text or media_info:
                        messages.append(msg_data)
                except:
                    pass
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
