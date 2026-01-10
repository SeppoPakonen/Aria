# Aria Plugin Architecture

This document outlines the proposed architecture for extending the Aria CLI through a modular plugin system.

## 1. Overview

Aria aims to be a flexible platform for web automation. An extensibility system allows third-party developers and users to add new capabilities without modifying the core codebase.

## 2. Extension Points

We have identified several key areas where plugins can extend Aria:

- **Commands:** Adding new top-level commands or subcommands to the `aria` CLI.
- **Navigators:** Providing alternative navigation strategies or supporting different browser automation engines.
- **Analyzers:** Custom AI-driven analysis or data extraction logic.
- **Exporters:** Support for new report formats (e.g., PDF, CSV, Excel).
- **Hooks:** Intercepting core events (e.g., before navigation, after page load).

## 3. Base Plugin Interface

All plugins should inherit from a common `BasePlugin` class.

```python
class BasePlugin:
    def __init__(self, context):
        self.context = context  # Access to AriaNavigator, ScriptManager, etc.

    def on_load(self):
        """Called when the plugin is first loaded."""
        pass

    def get_commands(self):
        """Returns a list of command definitions to be added to the CLI."""
        return []

    def get_hooks(self):
        """Returns a mapping of hook names to callback functions."""
        return {}
```

## 4. Hook System

Aria will provide a set of standard hooks that plugins can subscribe to:

- `pre_navigation(url)`: Triggered before `navigator.navigate(url)`.
- `post_navigation(url, success)`: Triggered after navigation completes.
- `pre_ai_generation(prompt)`: Triggered before sending a prompt to the LLM.
- `post_ai_generation(prompt, response)`: Triggered after receiving an AI response.
- `on_session_start(browser_name)`: Triggered when a new browser session is opened.

## 5. Plugin Discovery and Loading

Plugins are loaded from a dedicated directory. By default, Aria looks in `~/.aria/plugins/`, but this can be overridden using the `ARIA_PLUGINS_DIR` environment variable.

1. **Discovery:** Aria scans the plugins directory for `.py` files or Python packages (directories with an `__init__.py`).
2. **Initialization:** Aria dynamically imports each module and searches for subclasses of `BasePlugin`.
3. **Registration:** 
   - **Commands:** Plugins provide a list of command dictionaries. Each dictionary defines the command name, help text, arguments, and a callback function.
   - **Hooks:** Plugins provide a mapping of hook names to callback functions.

### Example Command Definition
```python
def get_commands(self):
    return [
        {
            "name": "hello",
            "help": "Prints a greeting",
            "arguments": [
                {"name": "--name", "type": str, "default": "World"}
            ],
            "callback": self.hello_callback
        }
    ]
```

## 6. Implementation Details

The `PluginManager` in `src/plugin_manager.py` handles the lifecycle of plugins. It is initialized during CLI startup and provides the `context` dictionary to each plugin.

### Context Object
The `context` provided to plugins includes:
- `navigator`: The `AriaNavigator` instance.
- `script_manager`: The `ScriptManager` instance.
- `safety_manager`: The `SafetyManager` instance.
- `report_manager`: The `ReportManager` instance.
- `version`: The current Aria version string.

## 6. Security Considerations

Plugins have significant power as they run with the same permissions as Aria.

- **Sandbox:** Ideally, plugins should run in a restricted environment, though this is challenging with native Python plugins.
- **User Confirmation:** Loading new plugins should require explicit user approval.
- **Review:** Users should be encouraged to review plugin code before installation.
