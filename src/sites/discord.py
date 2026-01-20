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
    """Scraper for Discord Web."""
    URL = "https://discord.com/app"

    def __init__(self, navigator: AriaNavigator, site_manager):
        self.navigator = navigator
        self.sm = site_manager
        self.site_name = "discord"

    def navigate(self):
        """Navigates to Discord."""
        print(f"Navigating to {self.URL}...")
        self.navigator.navigate(self.URL)
        
        try:
            print("Waiting for Discord to load...")
            # Look for the server list or home button
            self.navigator.wait_for_element("nav[aria-label='Servers'], nav[aria-label='Palvelimet']", by=By.CSS_SELECTOR, timeout=45)
            print("Discord loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load Discord: {e}")
            print("Error: Discord did not load. Please ensure you are logged in.")
            return False

    def refresh(self):
        """Orchestrates the Discord data refresh."""
        if "discord.com" not in self.navigator.driver.current_url:
            if not self.navigate():
                return False
        
        print("Starting data refresh for Discord...")
        
        # 1. Discover Servers
        servers = self.discover_servers()
        print(f"Found {len(servers)} servers.")
        
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
        """Finds all available servers in the left sidebar."""
        script = """
        const nav = document.querySelector('nav[aria-label="Servers"]') || 
                    document.querySelector('nav[aria-label="Palvelimet"]');
        if (!nav) return [];
        
        return Array.from(nav.querySelectorAll('div[data-list-item-id^="guildsnav_"]'))
            .map(el => ({
                id: el.getAttribute('data-list-item-id'),
                name: el.getAttribute('aria-label'),
                is_home: el.getAttribute('data-list-item-id').includes('home')
            }));
        """
        return self.navigator.driver.execute_script(script)

    def crawl_server(self, server):
        """Clicks a server and crawls its channels."""
        print(f"Switching to server: {server['name']}")
        
        # Click server
        click_script = f"document.querySelector('[data-list-item-id="{server['id']}"]').click();"
        self.navigator.driver.execute_script(click_script)
        time.sleep(3)
        
        # Discover channels
        channels = self.discover_channels()
        print(f"  Found {len(channels)} channels in {server['name']}")
        
        for channel in channels:
            if channel['type'] == 'text' and (channel['has_unread'] or self.is_history_empty(server, channel)):
                self.scrape_channel(server, channel)

    def discover_channels(self):
        """Finds all text channels in the current server."""
        script = """
        const sidebar = document.querySelector('nav[aria-label^="Channels"]') || 
                        document.querySelector('nav[aria-label^="Kanavat"]');
        if (!sidebar) return [];
        
        return Array.from(sidebar.querySelectorAll('li'))
            .map(li => {
                const link = li.querySelector('a[data-list-item-id^="channels_"]');
                if (!link) return null;
                
                const name = link.getAttribute('aria-label') || "";
                return {
                    id: link.getAttribute('data-list-item-id'),
                    name: name,
                    type: name.includes('#') ? 'text' : 'other',
                    has_unread: !!li.querySelector('[class*="unread"]')
                };
            }).filter(c => c !== null);
        """
        return self.navigator.driver.execute_script(script)

    def scrape_channel(self, server, channel):
        """Clicks a channel and extracts messages."""
        print(f"    Scraping channel: {channel['name']}")
        
        # Click channel
        click_script = f"document.querySelector('[data-list-item-id="{channel['id']}"]').click();"
        self.navigator.driver.execute_script(click_script)
        time.sleep(3)
        
        # Extract messages using BS4
        messages = self.extract_messages()
        
        # Save
        filename = f"chat_{self.safe_fn(server['name'])}_{self.safe_fn(channel['name'])}.json"
        self.sm.save_data(self.site_name, filename, {
            "server": server['name'],
            "channel": channel['name'],
            "scraped_at": time.ctime(),
            "messages": messages
        })

    def extract_messages(self):
        """Extracts messages from the active chat window."""
        from bs4 import BeautifulSoup
        try:
            # Discord messages are in a list with specific role or class
            main_html = self.navigator.driver.execute_script("return document.querySelector('main').innerHTML")
            soup = BeautifulSoup(main_html, 'html.parser')
            
            # This is a complex React structure, we'll need to refine selectors
            msg_elements = soup.select('li[class*="message_"]')
            messages = []
            
            for el in msg_elements:
                try:
                    # Discord often groups messages under one avatar
                    user = el.select_one('[class*="username_"]')
                    content = el.select_one('[class*="messageContent_"]')
                    ts = el.select_one('time')
                    
                    if content:
                        messages.append({
                            "user": user.get_text(strip=True) if user else "Continuation",
                            "text": content.get_text(strip=True),
                            "timestamp": ts.get('datetime') if ts else "Unknown"
                        })
                except:
                    continue
            return messages
        except:
            return []

    def is_history_empty(self, server, channel):
        filename = f"chat_{self.safe_fn(server['name'])}_{self.safe_fn(channel['name'])}.json"
        return self.sm.load_data(self.site_name, filename) is None

    def safe_fn(self, name):
        return "".join([c if c.isalnum() else "_" for c in name])
