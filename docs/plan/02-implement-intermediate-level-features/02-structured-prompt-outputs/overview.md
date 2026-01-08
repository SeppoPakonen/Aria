# Phase 02: Structured Prompt Outputs

## Goal
Generate more organized and machine-readable outputs from AI prompts, allowing the CLI to be used as part of larger automation pipelines and providing clearer information to the user.

## Tasks
1. **Task 01: Implement JSON output format**
   - Add a `--format json` flag to `page summarize` and `page new --prompt`.
   - Update the AI prompt logic to request a structured JSON response.
   - Implement basic parsing and validation of the JSON response.
2. **Task 02: Implement Markdown output format**
   - Add a `--format markdown` flag.
   - Ensure the AI returns well-formatted Markdown with headers, lists, and tables where appropriate.
3. **Task 03: Implement automatic format detection (Optional)**
   - If the prompt asks for a "list" or "table", automatically adjust the output format if not specified.

## Task 01: Implement JSON output format - Details
- **Input**: `aria page summarize --format json`
- **Process**:
  - Append instructions to the LLM: "Return the summary in valid JSON format with keys like 'summary', 'key_points', 'sentiment', etc."
  - Parse the AI response to ensure it's valid JSON.
- **Output**: The JSON string printed to the console.
