# Multi-Tab Interaction Patterns in Aria

Aria's strength lies in its ability to orchestrate interactions across multiple web pages. This document outlines advanced patterns for multi-tab workflows.

## 1. Parallel Information Extraction (The "Comparison" Pattern)

**Goal**: Compare specific attributes (price, features, availability) across multiple vendors or sources.

**Workflow**:
1.  Open tabs for each source:
    ```bash
    aria page new --url https://amazon.com/product...
    aria page new --url https://ebay.com/product...
    ```
2.  Tag each tab for easy reference:
    ```bash
    aria page 0 tag amazon
    aria page 1 tag ebay
    ```
3.  Execute a synthesis prompt across tagged tabs:
    ```bash
    aria page summarize "Compare the price and shipping time from tag:amazon and tag:ebay. Return a markdown table."
    ```

## 2. Cross-Reference & Validation (The "Consensus" Pattern)

**Goal**: Verify information by checking multiple authoritative sources.

**Workflow**:
1.  Perform searches on different platforms:
    ```bash
    aria page new --url "https://google.com/search?q=Aria+CLI+features"
    aria page new --url "https://twitter.com/search?q=Aria+CLI"
    ```
2.  Synthesize the results:
    ```bash
    aria page summarize "Based on the search results in tab 0 and tab 1, what are the top 3 most praised features of Aria? Highlight any discrepancies."
    ```

## 3. Sequential Pipeline (The "Chaining" Pattern)

**Goal**: Use data from one page to drive interaction on another.

**Workflow**:
1.  Find a data point on Page A:
    ```bash
    aria page new --url "https://example.com/item-details"
    # Use summarize to extract a specific ID or value
    aria page summarize "What is the SKU for this item?"
    ```
2.  Use that value in a new search or navigation on Page B:
    ```bash
    aria page new --url "https://competitor.com/search?q={{extracted_sku}}"
    ```
    *(Note: This pattern often involves the user or a script manager passing the parameter.)*

## 4. Aggregated Reporting (The "Synthesis" Pattern)

**Goal**: Create a comprehensive report from disparate sources.

**Workflow**:
1.  Open multiple research tabs.
2.  Generate a report that references all of them:
    ```bash
    aria report generate "Compile a technical summary of the technologies discussed in all open tabs. Include a 'Sources' section with URLs." --title "Tech Research Report" --format html
    ```

## Implementation Considerations

- **Context Limits**: Be mindful of the AI's context window when gathering content from many large pages.
- **Tab Identifiers**: Use stable IDs or tags rather than index numbers when writing long-running scripts.
- **Wait States**: Ensure pages are fully loaded before attempting to extract content or summarize.
