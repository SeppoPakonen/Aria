import os
import json
from logger import get_logger

logger = get_logger("script_manager")

class ScriptManager:
    def __init__(self):
        self.aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
        self.scripts_dir = os.path.join(self.aria_dir, "scripts")
        self.metadata_file = os.path.join(self.scripts_dir, "metadata.json")
        
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
        
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, "w") as f:
                json.dump({"scripts": []}, f)

    def _load_metadata(self):
        try:
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return {"scripts": []}

    def _save_metadata(self, metadata):
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f, indent=4)
        except IOError as e:
            logger.error(f"Failed to save metadata: {e}")

    def create_script(self, prompt: str, name: str = None) -> int:
        """Creates a new script from a prompt."""
        metadata = self._load_metadata()
        script_id = len(metadata["scripts"])
        
        if not name:
            name = f"script_{script_id}"
        
        script_entry = {
            "id": script_id,
            "name": name,
            "prompt": prompt,
            "type": "prompt"
        }
        
        metadata["scripts"].append(script_entry)
        self._save_metadata(metadata)
        logger.info(f"Created new script {script_id}: {prompt[:30]}...")
        return script_id

    def list_scripts(self) -> list[dict]:
        """Returns a list of all scripts."""
        metadata = self._load_metadata()
        return metadata["scripts"]

    def get_script(self, identifier) -> dict | None:
        """Returns a script by ID or name."""
        metadata = self._load_metadata()
        try:
            # Try by ID
            idx = int(identifier)
            for s in metadata["scripts"]:
                if s["id"] == idx:
                    return s
        except (ValueError, TypeError):
            # Try by name
            for s in metadata["scripts"]:
                if s["name"] == identifier:
                    return s
        return None

    def edit_script(self, identifier, prompt: str) -> bool:
        """Modifies the prompt of an existing script."""
        metadata = self._load_metadata()
        script = None
        try:
            idx = int(identifier)
            for s in metadata["scripts"]:
                if s["id"] == idx:
                    script = s
                    break
        except (ValueError, TypeError):
            for s in metadata["scripts"]:
                if s["name"] == identifier:
                    script = s
                    break
        
        if script:
            script["prompt"] = prompt
            self._save_metadata(metadata)
            logger.info(f"Edited script {identifier}")
            return True
        return False

    def remove_script(self, identifier: str) -> bool:
        """Deletes a script."""
        metadata = self._load_metadata()
        initial_count = len(metadata["scripts"])
        
        try:
            idx = int(identifier)
            metadata["scripts"] = [s for s in metadata["scripts"] if s["id"] != idx]
        except (ValueError, TypeError):
            metadata["scripts"] = [s for s in metadata["scripts"] if s["name"] != identifier]
        
        if len(metadata["scripts"]) < initial_count:
            # Re-index remaining scripts to keep IDs consistent with list indices if desired,
            # or just leave them. Runbook seems to imply stable IDs.
            # For simplicity, we won't re-index but new scripts will get higher IDs.
            self._save_metadata(metadata)
            logger.info(f"Removed script: {identifier}")
            return True
        return False

    def run_script(self, identifier: str, navigator=None) -> bool:
        """Executes a script."""
        script = self.get_script(identifier)
        if not script:
            print(f"Error: Script '{identifier}' not found.")
            return False
        
        print(f"Running script {script['id']}: {script['prompt']}")
        
        if script["type"] == "prompt":
            if navigator:
                navigator.navigate_with_prompt(script["prompt"])
                return True
            else:
                print("Error: Navigator not provided to run prompt script.")
                return False
        return False
