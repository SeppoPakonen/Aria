import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("aria.site_manager")

class SiteManager:
    """Manages site-specific data storage and retrieval."""
    def __init__(self, base_dir: str = None):
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = os.path.join(os.path.expanduser("~"), ".aria", "sites")
        
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)

    def get_site_dir(self, site_name: str) -> str:
        """Returns the directory path for a specific site."""
        site_dir = os.path.join(self.base_dir, site_name)
        if not os.path.exists(site_dir):
            os.makedirs(site_dir, exist_ok=True)
            # Create subdirectories for common data types
            os.makedirs(os.path.join(site_dir, "media"), exist_ok=True)
        return site_dir

    def save_data(self, site_name: str, filename: str, data: Any):
        """Saves data to a JSON file within a site's directory."""
        site_dir = self.get_site_dir(site_name)
        file_path = os.path.join(site_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved data to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save data to {file_path}: {e}")

    def load_data(self, site_name: str, filename: str) -> Optional[Any]:
        """Loads data from a JSON file within a site's directory."""
        file_path = os.path.join(self.get_site_dir(site_name), filename)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load data from {file_path}: {e}")
            return None

    def get_recent_items(self, site_name: str, filename: str, key: str = "items", limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves the most recent items from a JSON data file."""
        data = self.load_data(site_name, filename)
        if not data:
            return []
        
        # Assume data is a list or a dict with a list under 'key'
        items = data if isinstance(data, list) else data.get(key, [])
        
        # Simple heuristic: items at the end are often newer, 
        # but better would be sorting by a timestamp if available.
        # We'll try to find a timestamp field.
        timestamp_fields = ['timestamp', 'date', 'created_at', 'time']
        
        def get_ts(item):
            for field in timestamp_fields:
                if field in item:
                    return str(item[field])
            return ""

        try:
            sorted_items = sorted(items, key=get_ts, reverse=True)
            return sorted_items[:limit]
        except:
            return items[-limit:] # Fallback to last N items

    def list_sites(self) -> List[str]:
        """Lists all sites that have local data."""
        if not os.path.exists(self.base_dir):
            return []
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]

    def get_registry(self, site_name: str) -> Dict[str, Any]:
        """Returns the persistent registry for a site."""
        reg = self.load_data(site_name, "registry.json")
        return reg if reg else {"next_id": 1, "mappings": {}}

    def cleanup_old_data(self, site_name: str, days: int = 30) -> int:
        """Removes data files older than the specified number of days."""
        site_dir = self.get_site_dir(site_name)
        count = 0
        now = time.time()
        cutoff = now - (days * 86400)
        
        for f in os.listdir(site_dir):
            if f.endswith(".json") and f != "registry.json" and f != "metadata.json":
                file_path = os.path.join(site_dir, f)
                if os.path.getmtime(file_path) < cutoff:
                    try:
                        os.remove(file_path)
                        count += 1
                    except Exception as e:
                        logger.error(f"Failed to remove {file_path}: {e}")
        return count

    def archive_site(self, site_name: str, output_path: str = None) -> str:
        """Creates a ZIP archive of all data for a specific site."""
        import shutil
        site_dir = self.get_site_dir(site_name)
        if not os.path.exists(site_dir):
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not output_path:
            output_path = os.path.join(self.base_dir, f"archive_{site_name}_{timestamp}")
            
        if output_path.endswith(".zip"):
            output_path = output_path[:-4]
            
        final_path = shutil.make_archive(output_path, 'zip', site_dir)
        return final_path
