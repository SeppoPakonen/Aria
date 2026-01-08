import os

class ScriptManager:
    def __init__(self):
        self.scripts_dir = os.path.join(os.path.expanduser("~"), ".aria", "scripts")
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)

    def create_script(self, name: str) -> str | None:
        """Creates a new script file."""
        script_path = os.path.join(self.scripts_dir, f"{name}.py")
        if os.path.exists(script_path):
            print(f"Error: Script '{name}.py' already exists.")
            return None
        
        try:
            with open(script_path, "w") as f:
                # You can add a template here later if you want
                f.write("# Your new Aria script\n")
            return script_path
        except IOError as e:
            print(f"Error creating script file: {e}")
            return None

    def list_scripts(self) -> list[str]:
        """Returns a list of all script files."""
        try:
            files = os.listdir(self.scripts_dir)
            return [f for f in files if os.path.isfile(os.path.join(self.scripts_dir, f))]
        except OSError as e:
            print(f"Error listing scripts: {e}")
            return []

    def get_script_path(self, name: str) -> str | None:
        """Returns the full path of a script if it exists."""
        # Ensure we have the .py extension
        if not name.endswith(".py"):
            name += ".py"
        
        script_path = os.path.join(self.scripts_dir, name)
        if os.path.exists(script_path):
            return script_path
        return None

    def remove_script(self, name: str) -> bool:
        """Deletes a script file."""
        script_path = self.get_script_path(name)
        if script_path:
            try:
                os.remove(script_path)
                return True
            except OSError as e:
                print(f"Error deleting script: {e}")
                return False
        return False
