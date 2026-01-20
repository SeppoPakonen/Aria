import os
import json
import logging
from logger import get_logger

logger = get_logger("credential_manager")

class CredentialManager:
    def __init__(self):
        self.aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
        self.credentials_file = os.path.join(self.aria_dir, "credentials.json")
        
        if not os.path.exists(self.aria_dir):
            os.makedirs(self.aria_dir)
            
        if not os.path.exists(self.credentials_file):
            self._save_credentials({})
            # Set restrictive permissions on Linux/macOS
            if os.name != 'nt':
                try:
                    os.chmod(self.credentials_file, 0o600)
                except Exception as e:
                    logger.warning(f"Could not set restrictive permissions on {self.credentials_file}: {e}")

    def _load_credentials(self) -> dict:
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, "r") as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load credentials: {e}")
        return {}

    def _save_credentials(self, credentials: dict):
        try:
            with open(self.credentials_file, "w") as f:
                json.dump(credentials, f, indent=4)
        except IOError as e:
            logger.error(f"Failed to save credentials: {e}")

    def set_credential(self, key: str, value: str):
        """Sets a credential in the vault."""
        credentials = self._load_credentials()
        credentials[key] = value
        self._save_credentials(credentials)
        logger.info(f"Set credential: {key}")

    def get_credential(self, key: str) -> str | None:
        """Retrieves a credential from the vault."""
        credentials = self._load_credentials()
        return credentials.get(key)

    def list_keys(self) -> list[str]:
        """Lists all keys in the vault."""
        credentials = self._load_credentials()
        return list(credentials.keys())

    def remove_credential(self, key: str) -> bool:
        """Removes a credential from the vault."""
        credentials = self._load_credentials()
        if key in credentials:
            del credentials[key]
            self._save_credentials(credentials)
            logger.info(f"Removed credential: {key}")
            return True
        return False
