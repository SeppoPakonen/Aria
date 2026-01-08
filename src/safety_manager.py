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

    @staticmethod
    def confirm(message: str, default: bool = False) -> bool:
        """Prompts the user for confirmation."""
        suffix = " (Y/n)" if default else " (y/N)"
        try:
            response = input(f"{message}{suffix}: ").strip().lower()
            if not response:
                return default
            return response == 'y'
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return False
