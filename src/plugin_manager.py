import os
import importlib.util
import sys
import logging
from typing import List, Dict, Any, Callable

logger = logging.getLogger("aria.plugin_manager")

class BasePlugin:
    """Base class for all Aria plugins."""
    def __init__(self, context: Dict[str, Any]):
        self.context = context  # Access to AriaNavigator, ScriptManager, etc.

    def on_load(self):
        """Called when the plugin is first loaded."""
        pass

    def get_commands(self) -> List[Dict[str, Any]]:
        """
        Returns a list of command definitions to be added to the CLI.
        Each command definition should be a dictionary suitable for 
        subparsers.add_parser() and adding arguments.
        
        Example:
        [
            {
                "name": "hello",
                "help": "Prints hello world",
                "arguments": [
                    {"name": "--name", "type": str, "help": "Name to greet"}
                ],
                "callback": self.hello_callback
            }
        ]
        """
        return []

    def get_hooks(self) -> Dict[str, Callable]:
        """Returns a mapping of hook names to callback functions."""
        return {}

class PluginManager:
    """Manages discovery, loading, and registration of Aria plugins."""
    def __init__(self, plugins_dir: str = None, context: Dict[str, Any] = None):
        if plugins_dir is None:
            self.plugins_dir = os.environ.get("ARIA_PLUGINS_DIR", os.path.join(os.path.expanduser("~"), ".aria", "plugins"))
        else:
            self.plugins_dir = plugins_dir
            
        self.context = context or {}
        self.plugins: List[BasePlugin] = []
        self.hooks: Dict[str, List[Callable]] = {}

        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir, exist_ok=True)

    def load_plugins(self):
        """Scans the plugins directory and loads all valid Python plugins."""
        logger.info(f"Loading plugins from {self.plugins_dir}")
        
        if not os.path.isdir(self.plugins_dir):
            logger.warning(f"Plugins directory {self.plugins_dir} does not exist.")
            return

        # Add plugins directory to sys.path to allow imports within plugins
        if self.plugins_dir not in sys.path:
            sys.path.insert(0, self.plugins_dir)

        for item in os.listdir(self.plugins_dir):
            item_path = os.path.join(self.plugins_dir, item)
            
            # Load from .py files or directories (packages)
            module_name = None
            if os.path.isfile(item_path) and item.endswith(".py") and item != "__init__.py":
                module_name = item[:-3]
            elif os.path.isdir(item_path) and os.path.isfile(os.path.join(item_path, "__init__.py")):
                module_name = item

            if module_name:
                try:
                    self._load_module(module_name)
                except Exception as e:
                    logger.error(f"Failed to load plugin {module_name}: {e}", exc_info=True)

    def _load_module(self, module_name: str):
        """Imports a module and instantiates any BasePlugin subclasses found."""
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            logger.error(f"Could not find spec for module {module_name}")
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, BasePlugin) and 
                attr is not BasePlugin):
                
                plugin_instance = attr(self.context)
                self.register_plugin(plugin_instance)
                logger.info(f"Loaded plugin class: {attr_name} from {module_name}")

    def register_plugin(self, plugin: BasePlugin):
        """Registers a plugin instance and its hooks."""
        plugin.on_load()
        self.plugins.append(plugin)
        
        # Register hooks
        for hook_name, callback in plugin.get_hooks().items():
            if hook_name not in self.hooks:
                self.hooks[hook_name] = []
            self.hooks[hook_name].append(callback)

    def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Executes all callbacks registered for a given hook."""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing hook {hook_name} in plugin: {e}", exc_info=True)

    def get_plugin_commands(self) -> List[Dict[str, Any]]:
        """Collects all command definitions from loaded plugins."""
        all_commands = []
        for plugin in self.plugins:
            all_commands.extend(plugin.get_commands())
        return all_commands
