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
        """
        return []

    def get_hooks(self) -> Dict[str, Callable]:
        """Returns a mapping of hook names to callback functions."""
        return {}

    def get_ai_providers(self) -> Dict[str, Any]:
        """Returns a mapping of provider names to AI provider classes."""
        return {}

    def get_navigators(self) -> Dict[str, Any]:
        """Returns a mapping of navigator names to Navigator classes."""
        return {}

class BaseAIProvider:
    """Base class for AI providers."""
    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def generate(self, prompt: str, context: str = "", output_format: str = "text") -> str:
        """Generates a response from the AI."""
        raise NotImplementedError("AI providers must implement the generate method.")

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
        self.ai_providers: Dict[str, BaseAIProvider] = {}
        self.navigators: Dict[str, Any] = {}

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
        """Registers a plugin instance and its hooks/providers."""
        plugin.on_load()
        self.plugins.append(plugin)
        
        # Register hooks
        for hook_name, callback in plugin.get_hooks().items():
            if hook_name not in self.hooks:
                self.hooks[hook_name] = []
            self.hooks[hook_name].append(callback)

        # Register AI providers
        for name, provider_class in plugin.get_ai_providers().items():
            self.ai_providers[name] = provider_class(self.context)
            logger.info(f"Registered AI provider: {name}")

        # Register Navigators
        for name, nav_class in plugin.get_navigators().items():
            self.navigators[name] = nav_class
            logger.info(f"Registered Navigator: {name}")

    def get_ai_provider(self, name: str) -> BaseAIProvider:
        """Returns the registered AI provider for the given name."""
        return self.ai_providers.get(name)

    def list_ai_providers(self) -> List[str]:
        """Returns a list of all registered AI provider names."""
        return list(self.ai_providers.keys())

    def get_navigator(self, name: str) -> Any:
        """Returns the registered Navigator class for the given name."""
        return self.navigators.get(name)

    def list_navigators(self) -> List[str]:
        """Returns a list of all registered Navigator names."""
        return list(self.navigators.keys())

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
