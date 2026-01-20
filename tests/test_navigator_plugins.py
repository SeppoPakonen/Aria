import unittest
from unittest.mock import MagicMock
import sys
import os

from plugin_manager import PluginManager, BasePlugin
from navigator import BaseNavigator

class MockNavigator(BaseNavigator):
    def __init__(self):
        super().__init__()
        self.started = False
    
    def start_session(self, browser_name="chrome", headless=False, force=False):
        self.started = True
        return True

class MockNavPlugin(BasePlugin):
    def get_navigators(self):
        return {"mock": MockNavigator}

class TestNavigatorPlugins(unittest.TestCase):
    def test_navigator_registration(self):
        pm = PluginManager(context={})
        plugin = MockNavPlugin(context={})
        pm.register_plugin(plugin)
        
        self.assertIn("mock", pm.list_navigators())
        nav_class = pm.get_navigator("mock")
        self.assertEqual(nav_class, MockNavigator)
        
    def test_navigator_instantiation(self):
        # This is harder to test without running _run_cli, 
        # but we can verify the PluginManager part.
        pm = PluginManager(context={})
        pm.register_plugin(MockNavPlugin(context={}))
        
        nav_class = pm.get_navigator("mock")
        nav = nav_class()
        self.assertIsInstance(nav, MockNavigator)
        nav.start_session()
        self.assertTrue(nav.started)

if __name__ == "__main__":
    unittest.main()
