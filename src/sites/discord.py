import time
import logging
import re
import os
import json
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from navigator import AriaNavigator

logger = logging.getLogger("aria.sites.discord")

class DiscordScraper:
    """Scraper for Discord Web using language-agnostic data attributes."""
    URL = "https://discord.com/app"

    def __init__(self, navigator: AriaNavigator, site_manager):
        self.navigator = navigator
        self.sm = site_manager
        self.site_name = "discord"

    def navigate(self):
        """Navigates to Discord and waits for full load."""
        if "/channels/" in self.navigator.driver.current_url:
            return True

        print(f"Navigating to {self.URL}...")
        self.navigator.navigate(self.URL)
        
        try:
            print("Waiting for Discord to fully load...")
            # Wait for the app container
            self.navigator.wait_for_element("div[id='app-mount']", by=By.CSS_SELECTOR, timeout=45)
            # Wait specifically for the guild scroller
            self.navigator.wait_for_element("ul[data-list-id='guildsnav']", by=By.CSS_SELECTOR, timeout=20)
            time.sleep(3)
            print("Discord loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load Discord: {e}")
            print("Error: Discord did not load. Please ensure you are logged in.")
            return False

    def refresh(self):
        """Orchestrates the Discord data refresh."""
        if not self.navigate():
            return False
        
        print("Starting data refresh for Discord...")
        
        # 1. Discover Servers
        servers = self.discover_servers()
        if not any(s['is_home'] for s in servers):
            servers.insert(0, {"id": "guildsnav___home", "name": "Direct Messages", "is_home": True})
            
        print(f"Found {len(servers)} server containers.")
        
        # 2. Update Registry
        self.sm.update_registry(self.site_name, [s["name"] for s in servers])
        
        # 3. Crawl each server
        for server in servers:
            self.crawl_server(server)
            
        self.sm.save_data(self.site_name, "metadata.json", {
            "last_refresh": time.ctime(),
            "server_count": len(servers)
        })
        return True

    def discover_servers(self):
        """Finds all available servers in the left sidebar guild rail."""
        script = """
        const rail = document.querySelector('ul[data-list-id="guildsnav"]');
        if (!rail) return [];
        
        return Array.from(rail.querySelectorAll('div[data-list-item-id^="guildsnav___"]'))
            .map(el => {
                const id = el.getAttribute('data-list-item-id');
                const isHome = id.includes('home');
                const name = isHome ? "Direct Messages" : (el.getAttribute('aria-label') || id.split('___')[1]);
                return { id, name, is_home: isHome };
            });
        """
        return self.navigator.driver.execute_script(script)

    def crawl_server(self, server):
        """Clicks a server and crawls its channels."""
        print(f"Switching to server: {server['name']}")
        
        if server.get('is_home'):
            if "/channels/@me" not in self.navigator.driver.current_url:
                self.navigator.navigate("https://discord.com/channels/@me")
                time.sleep(5)
        else:
            # Click server via synthetic mouse events
            click_script = """
            const id = arguments[0];
            const el = document.querySelector(`[data-list-item-id="${id}"]`);
            if (el) {
                const events = ['mousedown', 'mouseup', 'click'];
                events.forEach(type => {
                    const ev = new MouseEvent(type, { view: window, bubbles: true, cancelable: true });
                    el.dispatchEvent(ev);
                });
                return true;
            }
            return false;
            """
            success = self.navigator.driver.execute_script(click_script, server['id'])
            if not success:
                print(f"  Warning: Could not click server {server['name']}")
                return
            time.sleep(5)
        
        # Discover channels
        channels = self.discover_channels(server.get('is_home', False))
        print(f"  Found {len(channels)} channels/DMs in {server['name']}")
        
        for channel in channels:
            if channel['type'] in ['text', 'dm']:
                # For heavy Discord scraping, we only refresh if unread or empty
                if channel['has_unread'] or self.is_history_empty(server, channel):
                    self.scrape_channel(server, channel)

    def discover_channels(self, is_home=False):
        """Finds all text channels or DMs using data attributes."""
        if is_home:
            script = """
            return Array.from(document.querySelectorAll('a[data-list-item-id^="private-channels-uid_"]'))
                .map(a => {
                    const id = a.getAttribute('data-list-item-id');
                    const label = a.getAttribute('aria-label') || "Unknown DM";
                    return { id, name: label, type: 'dm', has_unread: !!a.querySelector('[class*="unread"]') };
                });
            """
        else:
            script = """
            return Array.from(document.querySelectorAll('a[data-list-item-id^="channels_"]'))
                .map(a => {
                    const id = a.getAttribute('data-list-item-id');
                    const label = a.getAttribute('aria-label') || "";
                    const isText = id.includes('channel') || label.includes('#');
                    return {
                        id: id,
                        name: label,
                        type: isText ? 'text' : 'other',
                        has_unread: !!a.closest('li').querySelector('[class*="unread"]')
                    };
                }).filter(c => c !== null);
            """
        return self.navigator.driver.execute_script(script)

    def scrape_channel(self, server, channel):
        """Clicks a channel and extracts messages."""
        print(f"    Scraping channel: {channel['name']}")
        
        click_script = """
        const id = arguments[0];
        const el = document.querySelector(`a[data-list-item-id="${id}"]`);
        if (el) {
            const events = ['mousedown', 'mouseup', 'click'];
            events.forEach(type => {
                const ev = new MouseEvent(type, { view: window, bubbles: true, cancelable: true });
                el.dispatchEvent(ev);
            });
            return true;
        }
        return false;
        """
        self.navigator.driver.execute_script(click_script, channel['id'])
        time.sleep(3) 

        # Handle Age Restriction or other overlays
        handle_overlay_script = """
        // Find buttons that look like "Continue" or "Jatka"
        const buttons = Array.from(document.querySelectorAll('button'));
        const continueBtn = buttons.find(b => 
            b.innerText.toLowerCase().includes('jatka') || 
            b.innerText.toLowerCase().includes('continue')
        );
        if (continueBtn) {
            continueBtn.click();
            return true;
        }
        return false;
        """
        if self.navigator.driver.execute_script(handle_overlay_script):
            print("      Bypassed age restriction overlay.")
            time.sleep(3)
        
        messages = self.extract_messages()
        
        filename = f"chat_{self.safe_fn(server['name'])}_{self.safe_fn(channel['name'])}.json"
        self.sm.save_data(self.site_name, filename, {
            "server": server['name'],
            "channel": channel['name'],
            "scraped_at": time.ctime(),
            "messages": messages
        })

    def extract_messages(self):
        """Extracts messages from the active chat window using BeautifulSoup."""
        from bs4 import BeautifulSoup
        try:
            main_html = self.navigator.driver.execute_script("""
                const m = document.querySelector('main') || document.querySelector('div[class*="chatContent"]');
                return m ? m.innerHTML : null;
            """)
            if not main_html: return []
            
            soup = BeautifulSoup(main_html, 'html.parser')
            msg_elements = soup.select('li[id^="chat-messages-"]')
            messages = []
            
            for el in msg_elements:
                try:
                    user_el = el.select_one('span[class*="username"]') or el.select_one('div[class*="username"]')
                    user = user_el.get_text(strip=True) if user_el else "Continuation"
                    
                    content_el = el.select_one('div[id^="message-content-"]') or el.select_one('div[class*="messageContent"]')
                    text = content_el.get_text(strip=True) if content_el else ""
                    
                    ts_el = el.select_one('time')
                    ts = ts_el.get('datetime') if ts_el else "Unknown"
                    
                    if text or ts != "Unknown":
                        messages.append({
                            "user": user,
                            "text": text,
                            "timestamp": ts
                        })
                except:
                    continue
            return messages
        except Exception as e:
            logger.error(f"Error extracting Discord messages: {e}")
            return []

    def is_history_empty(self, server, channel):
        filename = f"chat_{self.safe_fn(server['name'])}_{self.safe_fn(channel['name'])}.json"
        return self.sm.load_data(self.site_name, filename) is None

    def safe_fn(self, name):
        return "".join([c if c.isalnum() else "_" for c in name])