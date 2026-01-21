import time
import logging
import re
import os
import json
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from navigator import AriaNavigator

logger = logging.getLogger("aria.sites.whatsapp")

class WhatsAppScraper:
    """Scraper for WhatsApp Web."""
    URL = "https://web.whatsapp.com/"

    def __init__(self, navigator: AriaNavigator, site_manager):
        self.navigator = navigator
        self.sm = site_manager
        self.site_name = "whatsapp"

    def navigate(self):
        """Navigates to WhatsApp Web."""
        print(f"Navigating to {self.URL}...")
        self.navigator.navigate(self.URL)
        
        try:
            print("Waiting for WhatsApp to load (ensure you are logged in)...")
            # Look for the search bar or chat list container
            self.navigator.wait_for_element("div[contenteditable='true']", by=By.CSS_SELECTOR, timeout=45)
            print("WhatsApp loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load WhatsApp: {e}")
            print("Error: WhatsApp did not load. Please ensure QR code is scanned.")
            return False

    def refresh(self, deep=False):
        """Orchestrates the WhatsApp data refresh."""
        # Navigation is handled by aria.py but we verify
        if "web.whatsapp.com" not in self.navigator.driver.current_url:
            if not self.navigate():
                return False
        
        print("Starting data refresh for WhatsApp...")
        conversations = self.scrape_all_conversations()
        
        # Update persistent registry
        self.sm.update_registry(self.site_name, [c["name"] for c in conversations])
        
        self.sm.save_data(self.site_name, "metadata.json", {
            "last_refresh": time.ctime(),
            "conversation_count": len(conversations)
        })
        return True

    def scrape_all_conversations(self):
        """Iterates through WhatsApp conversations and scrapes them."""
        # 1. Get initial list of chat rows from the sidebar
        script_rows = """
        const sidebar = document.querySelector('div[aria-label="Keskustelulista"]') || 
                        document.querySelector('div[aria-label="Chat list"]') ||
                        document.querySelector('#pane-side');
        if (!sidebar) return [];
        return Array.from(sidebar.querySelectorAll('div[role="row"]'))
            .map((r, i) => {
                const titleEl = r.querySelector('span[title]');
                return {
                    index: i,
                    title: titleEl ? titleEl.getAttribute('title') : "Unknown"
                };
            })
            .filter(info => info.title !== "Unknown");
        """
        chat_info = self.navigator.driver.execute_script(script_rows)
        print(f"Found {len(chat_info)} conversation threads in sidebar.")
        
        all_data = []
        
        for info in chat_info[:15]: # Limit to first 15
            name = info["title"]
            print(f"Scraping conversation: {name}")
            
            try:
                # Click via synthetic events to trigger WhatsApp state change
                click_script = """
                const name = arguments[0];
                const xpath = `//span[@title=${JSON.stringify(name)}]`;
                let el;
                try {
                    el = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                } catch(e) {
                    el = Array.from(document.querySelectorAll('span[title]')).find(s => s.getAttribute('title') === name);
                }

                if (el) {
                    const events = ['mousedown', 'mouseup', 'click'];
                    events.forEach(type => {
                        const ev = new MouseEvent(type, {
                            view: window,
                            bubbles: true,
                            cancelable: true
                        });
                        el.dispatchEvent(ev);
                    });
                    return "CLICKED";
                }
                return "NOT_FOUND";
                """
                status = self.navigator.driver.execute_script(click_script, name)
                if (status == "NOT_FOUND"):
                    print(f"Warning: Could not find clickable element for {name}")
                    continue
                
                # Wait and verify that the chat header updated
                header_verified = False
                header_name = "None"
                for _ in range(12): # 12 seconds max
                    time.sleep(1)
                    header_name = self.navigator.driver.execute_script("""
                        const main = document.querySelector('div#main');
                        if (!main) return "MAIN_NOT_FOUND";
                        const titleSpan = main.querySelector('header span._ao3e');
                        return titleSpan ? titleSpan.innerText.trim() : "TITLE_NOT_FOUND";
                    """)
                    if (header_name == name):
                        header_verified = True
                        break
                
                if not header_verified:
                    print(f"Warning: Could not verify chat header for {name}. Got '{header_name}'. Data might be misattributed.")

                # Extract messages
                messages = self.extract_active_chat_messages()
                
                convo_data = {
                    "name": name,
                    "scraped_at": time.ctime(),
                    "messages": messages
                }
                
                # Save individual conversation file
                file_safe_name = "".join([c if c.isalnum() else "_" for c in name])
                self.sm.save_data(self.site_name, f"convo_{file_safe_name}.json", convo_data)
                
                all_data.append({"name": name, "message_count": len(messages)})
            except Exception as e:
                logger.error(f"Error scraping WhatsApp conversation {name}: {e}")
        
        # Save the master list
        self.sm.save_data(self.site_name, "conversations.json", all_data)
        return all_data

    def extract_active_chat_messages(self):
        """Extracts messages from the currently open WhatsApp chat area."""
        from bs4 import BeautifulSoup
        messages = []
        try:
            # Find the message list container (div#main to avoid SVG mask collision)
            script_main = """
            const mainDiv = document.querySelector('div#main');
            if (!mainDiv) return null;
            const areas = Array.from(mainDiv.querySelectorAll('div.copyable-area'));
            if (areas.length === 0) return mainDiv.innerHTML;
            const main = areas.sort((a,b) => b.innerHTML.length - a.innerHTML.length)[0];
            return main ? main.innerHTML : null;
            """
            main_html = self.navigator.driver.execute_script(script_main)
            if not main_html:
                return []

            soup = BeautifulSoup(f"<div>{main_html}</div>", 'html.parser')
            # WhatsApp uses 'message-in' and 'message-out' classes
            msg_containers = soup.select("div.message-in, div.message-out")
            
            for container in msg_containers:
                try:
                    # Identify if outgoing
                    is_outgoing = 'message-out' in container.get('class', [])
                    
                    # 1. Extract Text
                    text_el = container.select_one(".copyable-text span") or container.select_one("span._ao3e")
                    text = text_el.get_text(strip=True) if text_el else ""
                    
                    # 2. Extract Timestamp
                    # Format found: [21.06, 31.8.2025] Laura:
                    copyable_el = container.select_one(".copyable-text")
                    timestamp = "Unknown"
                    if copyable_el and copyable_el.has_attr("data-pre-plain-text"):
                        meta = copyable_el["data-pre-plain-text"]
                        match = re.search(r"\[(\d{1,2}[\.:]\d{2})", meta)
                        if match:
                            timestamp = match.group(1)
                    
                    if not text:
                        img_caption = container.select_one("span[dir='auto']")
                        if img_caption:
                            text = img_caption.get_text(strip=True)

                    if text or timestamp != "Unknown":
                        messages.append({
                            "text": text or "[Media/Empty]",
                            "timestamp": timestamp,
                            "type": "sent" if is_outgoing else "received"
                        })
                except:
                    continue
        except Exception as e:
            logger.error(f"Error extracting WhatsApp messages: {e}")
            
        return messages