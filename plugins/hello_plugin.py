from plugin_manager import BasePlugin

class HelloPlugin(BasePlugin):
    def on_load(self):
        pass

    def get_commands(self):
        return [
            {
                "name": "hello",
                "help": "A simple hello world plugin command",
                "arguments": [
                    {"name": "--name", "type": str, "default": "World", "help": "Name to greet"}
                ],
                "callback": self.hello_callback
            }
        ]

    def hello_callback(self, args):
        print(f"Hello, {args.name}! This is coming from a plugin.")
        print(f"Aria Version: {self.context.get('version')}")

    def get_hooks(self):
        return {
            "pre_navigation": self.on_pre_navigation,
            "post_navigation": self.on_post_navigation
        }

    def on_pre_navigation(self, url):
        print(f"[Plugin Hook] About to navigate to: {url}")

    def on_post_navigation(self, url, success):
        status = "successfully" if success else "with error"
        print(f"[Plugin Hook] Navigation to {url} completed {status}.")
