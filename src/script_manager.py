import os
import json
from logger import get_logger, time_it, add_secret, redact
from exceptions import ScriptError
from credential_manager import CredentialManager

logger = get_logger("script_manager")

class ScriptManager:
    def __init__(self):
        self.aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
        self.scripts_dir = os.path.join(self.aria_dir, "scripts")
        self.metadata_file = os.path.join(self.scripts_dir, "metadata.json")
        self.credential_manager = CredentialManager()
        
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

    @time_it(logger)
    def run_script(self, identifier: str, navigator=None, parameters=None) -> bool:
        """Executes a script."""
        script = self.get_script(identifier)
        if not script:
            raise ScriptError(f"Script '{identifier}' not found.")
        
        prompt = script['prompt']
        placeholders = self.get_script_placeholders(prompt)
        
        if placeholders:
            if parameters is None:
                parameters = {}
            
            # Use provided parameters and prompt for missing ones
            for placeholder in placeholders:
                if placeholder.startswith("env:"):
                    env_var = placeholder[4:]
                    val = os.environ.get(env_var)
                    if val is None:
                        logger.warning(f"Environment variable '{env_var}' not found for placeholder '{{{{{placeholder}}}}}'.")
                        if placeholder not in parameters:
                            if os.environ.get("ARIA_NON_INTERACTIVE") == "true":
                                raise ScriptError(f"Missing environment variable '{env_var}' for non-interactive run.")
                            import getpass
                            val = getpass.getpass(f"Enter value for environment variable '{env_var}': ")
                            parameters[placeholder] = val
                    else:
                        parameters[placeholder] = val
                    if parameters.get(placeholder):
                        add_secret(parameters[placeholder])
                elif placeholder.startswith("vault:"):
                    vault_key = placeholder[6:]
                    val = self.credential_manager.get_credential(vault_key)
                    if val is None:
                        logger.warning(f"Vault key '{vault_key}' not found for placeholder '{{{{{placeholder}}}}}'.")
                        if placeholder not in parameters:
                            if os.environ.get("ARIA_NON_INTERACTIVE") == "true":
                                raise ScriptError(f"Missing vault key '{vault_key}' for non-interactive run.")
                            import getpass
                            val = getpass.getpass(f"Enter value for vault key '{vault_key}': ")
                            parameters[placeholder] = val
                            if val and input(f"Save '{vault_key}' to vault? (y/n): ").lower() == 'y':
                                self.credential_manager.set_credential(vault_key, val)
                    else:
                        parameters[placeholder] = val
                    if parameters.get(placeholder):
                        add_secret(parameters[placeholder])
                elif placeholder not in parameters:
                    if os.environ.get("ARIA_NON_INTERACTIVE") == "true":
                        raise ScriptError(f"Missing parameter '{{{{{placeholder}}}}}' for non-interactive run.")
                    val = input(f"Enter value for '{{{{{placeholder}}}}}': ")
                    parameters[placeholder] = val
            
            prompt = self.apply_parameters(prompt, parameters)

        print(f"Running script {script['id']}: {redact(prompt)}")
        
        if script["type"] == "prompt":
            if navigator:
                navigator.navigate_with_prompt(prompt)
                return True
            else:
                raise ScriptError("Navigator not provided to run prompt script.")
        return False

    def get_script_placeholders(self, prompt: str) -> list[str]:
        """Returns a list of unique placeholders in the format {{name}} found in the prompt."""
        import re
        matches = re.findall(r"\{\{([a-zA-Z0-9_:-]+)\}\}", prompt)
        # Use dict.fromkeys to preserve order and remove duplicates
        return list(dict.fromkeys(matches))

    def apply_parameters(self, prompt: str, parameters: dict) -> str:
        """Replaces placeholders in the prompt with provided values."""
        import re
        result = prompt
        for key, value in parameters.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
