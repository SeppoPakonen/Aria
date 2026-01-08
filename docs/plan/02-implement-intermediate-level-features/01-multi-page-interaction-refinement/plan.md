# Phase 01: Multi-Page Interaction Refinement

## Goal
Enable the CLI to synthesize and process information across multiple open tabs/pages, allowing for complex queries that involve data from different sources.

## Tasks
1. **[DONE] Task 01: Implement cross-tab content synthesis**
   - Enhance prompt processing to identify references to other tabs (e.g., "tab 0", "tab 1").
   - Update `navigator` to efficiently retrieve content from multiple tabs.
   - Implement the synthesis logic using the Gemini API to combine information from referenced tabs based on the user's prompt.
2. **[TODO] Task 02: Improve tab selection and persistence**
   - Ensure `tab_id` handling is robust across different browser sessions.
   - Implement better heuristics for matching titles or URLs in `goto` commands.
3. **[TODO] Task 03: Implement basic tab grouping/tagging (Optional)**
   - Allow users to "tag" tabs for easier reference in prompts (e.g., "tag:news").

## Task 01: Implement cross-tab content synthesis - Details
- **Input**: A prompt containing references like `tab N` where N is the index from `page list`.
- **Process**:
  - Parse the prompt for `tab \d+`.
  - Fetch text content from all specified tabs.
  - Construct a comprehensive prompt for the LLM: "Using the following context from different tabs, answer the user's request: [Context...] Request: [Prompt]".
  - Handle cases where tabs don't exist or are empty.
- **Output**: The synthesized response printed to the console.
