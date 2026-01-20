import unittest
from unittest.mock import MagicMock
import sys

from plugin_manager import PluginManager, BasePlugin, BaseAIProvider
from aria import generate_ai_response

class MockAIProvider(BaseAIProvider):
    def generate(self, prompt, context="", output_format="text"):
        return f"Mocked response for: {prompt}"

class MockAIPlugin(BasePlugin):
    def get_ai_providers(self):
        return {"mock": MockAIProvider}

class TestAIPlugins(unittest.TestCase):
    def test_provider_registration(self):
        pm = PluginManager(context={})
        plugin = MockAIPlugin(context={})
        pm.register_plugin(plugin)
        
        self.assertIn("mock", pm.list_ai_providers())
        provider = pm.get_ai_provider("mock")
        self.assertIsInstance(provider, MockAIProvider)
        
    def test_generate_with_mock_provider(self):
        pm = PluginManager(context={})
        plugin = MockAIPlugin(context={})
        pm.register_plugin(plugin)
        
        response = generate_ai_response("Hello", plugin_manager=pm, provider_name="mock")
        self.assertEqual(response, "Mocked response for: Hello")

    def test_fallback_to_gemini(self):
        # We need to be careful here because Gemini requires an API key
        # But our refactored generate_ai_response has a fallback logic
        pm = PluginManager(context={})
        # If no GEMINI_API_KEY is set, it should return an error string
        # but it should still attempt to use GeminiProvider
        response = generate_ai_response("Hello", plugin_manager=pm, provider_name="gemini")
        self.assertIn("GEMINI_API_KEY", response)

if __name__ == "__main__":
    unittest.main()
