import os
import json
import sys

class SafetyManager:
    def __init__(self):
        self.aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
        self.safety_file = os.path.join(self.aria_dir, "safety.json")
        if not os.path.exists(self.aria_dir):
            os.makedirs(self.aria_dir)
        
        self.disclaimer_text = """
********************************************************************************
                                SAFETY DISCLAIMER
********************************************************************************
Aria is a web automation tool. By using this software, you agree to the following:

1. RESPONSIBILITY: You are solely responsible for your use of this tool and any 
   consequences thereof.
2. COMPLIANCE: You must comply with the Terms of Service of any website you 
   automate. Many websites prohibit or restrict automated access.
3. SECURITY: Never share your API keys or sensitive credentials. Automation 
   scripts can potentially expose private data if not handled carefully.
4. NO WARRANTY: This software is provided "as is", without warranty of any kind. 
   The authors are not liable for any damages, legal issues, or account bans 
   resulting from its use.

********************************************************************************
"""
        self.sensitive_patterns = [
            r"bank", r"paypal", r"stripe", r"crypto", r"coinbase",
            r"health", r"medical", r"patient",
            r"login", r"signin", r"auth", r"password",
            r"account", r"billing", r"checkout", r"payment",
            r"mail\.google\.com", r"outlook\.live\.com", r"proton\.me"
        ]

    def _is_disclaimer_accepted(self) -> bool:
        """Checks if the disclaimer has already been accepted."""
        if os.path.exists(self.safety_file):
            try:
                with open(self.safety_file, 'r') as f:
                    data = json.load(f)
                    return data.get("disclaimer_accepted", False)
            except (json.JSONDecodeError, IOError):
                return False
        return False

    def _save_acceptance(self):
        """Saves the disclaimer acceptance to the safety file."""
        try:
            with open(self.safety_file, 'w') as f:
                json.dump({"disclaimer_accepted": True}, f)
        except IOError as e:
            print(f"Error saving safety configuration: {e}")

    def ensure_disclaimer_accepted(self):
        """Ensures the disclaimer is accepted, prompting the user if necessary."""
        if self._is_disclaimer_accepted():
            return

        if os.environ.get("ARIA_NON_INTERACTIVE") == "true":
            print("Non-interactive mode: Auto-accepting disclaimer.")
            self._save_acceptance()
            return

        print(self.disclaimer_text)
        try:
            response = input("Do you accept these terms? (y/N): ").strip().lower()
            if response == 'y':
                self._save_acceptance()
                print("Disclaimer accepted. This will not be shown again.")
            else:
                print("Disclaimer rejected. Aria cannot proceed without your acceptance.")
                sys.exit(1)
        except EOFError:
            print("\nInput interrupted. Aria cannot proceed.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nAborted.")
            sys.exit(1)

    def get_security_best_practices(self) -> str:
        """Returns a summarized version of security best practices."""
        return """
Aria Security Best Practices Summary
====================================

1. API KEYS: Use environment variables (e.g., GEMINI_API_KEY). Never hardcode secrets.
2. SENSITIVE SITES: Avoid using Aria on banking, healthcare, or private email sites.
3. DATA PRIVACY: Be aware that page content is sent to external LLM providers.
4. SCRIPT SAFETY: Review third-party scripts before running them.
5. SANDBOXING: Run Aria in a controlled environment for maximum safety.

For full documentation, see: docs/security_best_practices.md
"""

    def is_sensitive_url(self, url: str) -> bool:
        """Checks if a URL matches any sensitive patterns."""
        import re
        url_lower = url.lower()
        for pattern in self.sensitive_patterns:
            if re.search(pattern, url_lower):
                return True
        return False

    def check_url_safety(self, url: str, force: bool = False) -> bool:
        """
        Checks URL safety and prompts user if sensitive.
        Returns True if safe to proceed, False otherwise.
        """
        if not self.is_sensitive_url(url):
            return True

        print(f"\n[WARNING] The URL '{url}' appears to be a sensitive site.")
        print("Automating interactions with banking, login, or private data sites is risky.")
        
        if force:
            print("Proceeding due to --force flag.")
            return True

        return self.confirm("Do you want to proceed anyway?", default=False)

    @staticmethod
    def confirm(message: str, default: bool = False) -> bool:
        """Prompts the user for confirmation."""
        if os.environ.get("ARIA_NON_INTERACTIVE") == "true":
            print(f"Non-interactive mode: Auto-responding with {'Yes' if default else 'No'} to: {message}")
            return default

        suffix = " (Y/n)" if default else " (y/N)"
        try:
            response = input(f"{message}{suffix}: ").strip().lower()
            if not response:
                return default
            return response == 'y'
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return False
