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
