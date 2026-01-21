import time
import logging
import re
import os
import json
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from navigator import AriaNavigator

logger = logging.getLogger("aria.sites.youtube_studio")

class YouTubeStudioScraper:
    """Scraper for YouTube Studio analytics and video data."""
    URL = "https://studio.youtube.com/"

    def __init__(self, navigator: AriaNavigator, site_manager):
        self.navigator = navigator
        self.sm = site_name = "youtube-studio"
        self.sm = site_manager
        self.site_name = "youtube-studio"

    def navigate(self):
        """Navigates to YouTube Studio and waits for load."""
        if "studio.youtube.com" in self.navigator.driver.current_url:
            return True

        print(f"Navigating to {self.URL}...")
        self.navigator.navigate(self.URL)
        
        try:
            print("Waiting for YouTube Studio to load...")
            # Wait for dashboard content
            self.navigator.wait_for_element('ytcp-app', by=By.TAG_NAME, timeout=45)
            time.sleep(5)
            print("YouTube Studio loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load YouTube Studio: {e}")
            print("Error: YouTube Studio did not load. Please ensure you are logged in.")
            return False

    def refresh(self):
        """Orchestrates the YouTube Studio data refresh."""
        if not self.navigate():
            return False
        
        print("Starting data refresh for YouTube Studio...")
        
        # 1. Scrape Dashboard Analytics
        analytics = self.scrape_dashboard()
        
        # 2. Scrape Video List
        videos = self.scrape_videos()
        
        self.sm.save_data(self.site_name, "analytics.json", analytics)
        self.sm.save_data(self.site_name, "videos.json", videos)
        self.sm.save_data(self.site_name, "metadata.json", {
            "last_refresh": time.ctime(),
            "video_count": len(videos)
        })
        return True

    def scrape_dashboard(self):
        """Extracts high-level channel analytics from the dashboard."""
        try:
            main_html = self.navigator.driver.page_source
            soup = BeautifulSoup(main_html, 'html.parser')
            
            analytics = {}
            # Look for summary cards
            summary_cards = soup.select('ytcp-video-snapshot, ytcp-channel-snapshot')
            for card in summary_cards:
                text = card.get_text(strip=True, separator=' ')
                analytics["channel_summary"] = text
                
            return analytics
        except Exception as e:
            logger.error(f"Error scraping dashboard: {e}")
            return {}

    def scrape_videos(self):
        """Extracts video details from the current page (dashboard or video list)."""
        print("  Extracting videos from current view...")
        try:
            main_html = self.navigator.driver.execute_script("""
                const main = document.querySelector('ytcp-video-list') || 
                             document.querySelector('#video-list') || 
                             document.querySelector('ytcp-app') ||
                             document.body;
                return main.innerHTML;
            """)
            soup = BeautifulSoup(main_html, 'html.parser')
            
            videos = []
            # Look for elements that contain video titles
            # On dashboard they are often in #video-title spans
            title_els = soup.select('[id*="video-title"], [class*="video-title"]')
            for el in title_els:
                title = el.get_text(strip=True)
                if not title or len(title) < 3: continue
                
                # Heuristic for views: find the first number in the surrounding text area
                views = "0"
                container = el.find_parent('div', class_=True) or el.parent.parent
                if container:
                    text = container.get_text(strip=True, separator=' ')
                    # Look for view counts (numbers) that aren't the title itself
                    # In Finnish: "203 katselukertaa"
                    nums = re.findall(r"(\d+)", text)
                    for n in nums:
                        if n != title and int(n) > 0:
                            views = n
                            break

                videos.append({
                    "title": title,
                    "views": views
                })
            
            # Deduplicate by title
            seen = set()
            unique_videos = []
            for v in videos:
                if v['title'] not in seen:
                    unique_videos.append(v)
                    seen.add(v['title'])
                    
            return unique_videos
        except Exception as e:
            logger.error(f"Error scraping videos: {e}")
            return []
