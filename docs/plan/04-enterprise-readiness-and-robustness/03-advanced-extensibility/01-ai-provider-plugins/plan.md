# Task: AI Provider Plugins

## Outcome
A pluggable AI generation system where users can choose between different LLM backends (Gemini, OpenAI, etc.) registered by plugins.

## Requirements
- `BaseAIProvider` class in `src/plugin_manager.py` (or a new `src/ai_providers.py`).
- Registry for AI providers in `PluginManager`.
- Update `generate_ai_response` to delegate to a selected provider.
- Implement `GeminiProvider` as the default, built-in provider.
- Example plugin showing how to add a dummy AI provider.

## Implementation Steps
1. **Define `BaseAIProvider`**:
   - `generate(prompt, context, format)` method.
2. **Update `PluginManager`**:
   - Add `register_ai_provider(name, provider)`.
   - Add `get_ai_provider(name)`.
   - Add `list_ai_providers()`.
3. **Refactor `src/aria.py`**:
   - Move Gemini logic to `GeminiProvider`.
   - Update `generate_ai_response` to use `plugin_manager.get_ai_provider()`.
   - Add a CLI flag `--provider` to select the backend.
4. **Tests**:
   - Verify that multiple providers can be registered and used.

## Acceptance Criteria
- `aria page new --prompt "test" --provider gemini` works as before.
- A plugin can register a new provider name.
- `aria page new --prompt "test" --provider my-custom-provider` uses the plugin's logic.
