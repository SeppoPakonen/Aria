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
                    # Identify sender (usually by looking for classes or position)
                    # This is a heuristic and might need adjustment based on Google's DOM
                    text = msg_el.find_element(By.CSS_SELECTOR, ".text-msg").text.strip()
                    
                    # Try to find timestamp
                    try:
                        timestamp = msg_el.find_element(By.CSS_SELECTOR, ".timestamp").text.strip()
                    except:
                        timestamp = "Unknown"
                        
                    # Check for outgoing/incoming status
                    is_outgoing = "outgoing" in msg_el.get_attribute("class")
                    
                    messages.append({
                        "text": text,
                        "timestamp": timestamp,
                        "type": "sent" if is_outgoing else "received"
                    })
                except:
                    # Could be a non-text message (media, etc.)
                    pass
        except Exception as e:
            logger.error(f"Error extracting messages: {e}")
            
        return messages
