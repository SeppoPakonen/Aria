# 50-recipes.md

This runbook provides a "cookbook" of end-to-end scenarios, demonstrating how to combine various `aria` commands to achieve complex goals. Each recipe includes a goal, copy/paste-friendly commands, expected results, and tips or variations.

## Recipes

### 1. Research and Summarize Multiple Sources

*   **Goal**: Research a specific topic across several reputable news sources and get a consolidated summary.
*   **Commands**:
    ```bash
    # 1. Open Firefox
    aria open firefox
    # 2. Open page for BBC News
    aria page new --url="https://www.bbc.com/news"
    # 3. Open page for The New York Times
    aria page new --url="https://www.nytimes.com"
    # 4. Open page for Al Jazeera
    aria page new --url="https://www.aljazeera.com"
    # 5. List pages to get tab IDs
    aria page list
    # (Example: 0: BBC, 1: NYT, 2: Al Jazeera)
    # 6. For each page, search and summarize "impact of AI on job market"
    aria page 0 goto --prompt="impact of AI on job market"
    aria page 0 summarize "Summarize the BBC perspective on AI's job market impact."

    aria page 1 goto --prompt="impact of AI on job market"
    aria page 1 summarize "Summarize The New York Times perspective on AI's job market impact."

    aria page 2 goto --prompt="impact of AI on job market"
    aria page 2 summarize "Summarize Al Jazeera's perspective on AI's job market impact."

    # 7. Open a new tab and ask aria to synthesize the information
    aria page new --prompt="Compare and contrast the summaries from the BBC, NYT, and Al Jazeera regarding AI's impact on the job market. Identify common themes and major differences."
    ```
*   **Expected Results**: Individual summaries from each news source, followed by a consolidated comparison in a new `aria` tab.
*   **Tips / Variations**:
    *   Use `tab_id` instead of `tab_num` for increased robustness if you anticipate closing or reordering tabs.
    *   Redirect summaries to a file if they are lengthy.

### 2. Local Report Generation via Bookmarks/Local Scopes

*   **Goal**: Find a specific document in bookmarks, then generate a local report based on its content or related local files.
*   **Commands**:
    ```bash
    # 1. Open Chrome
    aria open chrome
    # 2. Use bookmarks scope to find a specific project planning document
    aria page new --scope=bookmarks --prompt="Project Quantum Q3 Planning Doc"
    # (Assume this opens on tab 0)
    # 3. Use local scope to find related meeting notes on your file system
    aria page new --scope=local --prompt="find all meeting notes related to 'Project Quantum' in my documents folder"
    # (Assume this opens on tab 1)
    # 4. Open a new tab and synthesize a summary of both sources
    aria page new --prompt="Based on the 'Project Quantum Q3 Planning Doc' (tab 0) and the meeting notes (tab 1), provide a summary of key decisions made and next steps."
    ```
*   **Expected Results**: The project document and local meeting notes are opened in separate tabs. A new tab then provides a synthesized summary based on both.
*   **Tips / Variations**:
    *   Specify file types in local scope prompts (e.g., "find all .docx meeting notes").
    *   Instruct `aria` to highlight discrepancies between the planning doc and meeting notes.

### 3. Run a Script, then Summarize the Resulting Page

*   **Goal**: Execute a predefined `aria` script, and then, without creating another script, analyze the output.
*   **Commands**:
    ```bash
    # Assume script 0 exists and searches for "latest renewable energy breakthroughs"
    # You can create it like this:
    # aria script new --prompt="search for latest renewable energy breakthroughs"
    #
    # 1. Run the script (this will open a new page with search results)
    aria script 0 run # (assuming 'run' is an extrapolated command pattern, or it implies 'goto --prompt')
    # If 'aria script 0 run' is not available, you would manually recreate the prompt:
    # aria page new --prompt="search for latest renewable energy breakthroughs"
    # 2. List pages to confirm which tab holds the results (e.g., tab 0)
    aria page list
    # 3. Summarize the content of the results page
    aria page 0 summarize "What are the most promising breakthroughs mentioned on this page?"
    ```
*   **Expected Results**: A new browser tab showing search results, followed by a summary of those results in the terminal.
*   **Tips / Variations**:
    *   If the script's prompt causes navigation, ensure you're summarizing the correct `tab_num` or `tab_id`.

### 4. Multi-tab Workflow: Open 3 Tabs, Compare Summaries, Output Decision Notes

*   **Goal**: Research three different product options, compare their pros/cons, and get `aria` to help make a decision.
*   **Commands**:
    ```bash
    # 1. Open Product A page
    aria page new --url="https://example-shop.com/productA"
    # 2. Open Product B page
    aria page new --url="https://example-shop.com/productB"
    # 3. Open Product C page
    aria page new --url="https://example-shop.com/productC"
    # 4. List pages to confirm IDs (e.g., A=0, B=1, C=2)
    aria page list
    # 5. Get summaries for each product focusing on pros and cons
    aria page 0 summarize "What are the main pros and cons of Product A?"
    aria page 1 summarize "What are the main pros and cons of Product B?"
    aria page 2 summarize "What are the main pros and cons of Product C?"
    # 6. Open a new tab and ask for a comparative analysis and recommendation
    aria page new --prompt="Based on the pros and cons of Product A (tab 0), Product B (tab 1), and Product C (tab 2), which product offers the best value for money for a typical home user? Explain your reasoning."
    ```
*   **Expected Results**: Summaries for each product, followed by a comparative analysis and a recommendation based on the criteria.
*   **Tips / Variations**:
    *   You can refine the comparison prompt if the initial recommendation isn't satisfactory.

### 5. Automated Daily News Digest

*   **Goal**: Get a daily digest of specific news categories from preferred sources.
*   **Commands**:
    ```bash
    # This scenario is best achieved with a script.
    # Create the script once:
    # aria script new --prompt="open Google News, search 'global economic trends', then 'climate change policy', summarize top 3 articles from each search and compile into a single digest."
    # (Assume this creates script 0)

    # 1. Open Chrome
    aria open chrome
    # 2. Run the daily digest script
    aria script 0 run # (or aria page new --prompt="open Google News..." if 'run' is not direct)
    # 3. Once the digest is generated in a new tab (e.g., tab 0)
    aria page 0 summarize "Extract the most critical headlines and their implications."
    ```
*   **Expected Results**: A curated digest of news articles in a browser tab, further summarized to extract critical information.
*   **Tips / Variations**:
    *   Schedule this script to run daily using cron (Linux/macOS) or Task Scheduler (Windows).

### 6. Interactive Troubleshooting Session

*   **Goal**: Use `aria` to diagnose an issue on a web page step-by-step.
*   **Commands**:
    ```bash
    # 1. Open the problematic page
    aria page new --url="https://problematic-website.com/login"
    # 2. Ask aria for common issues on the page
    aria page 0 summarize "What are common reasons for login failures on this type of page (e.g., form issues, network problems)?"
    # 3. Based on the answer, investigate further. For example, if it suggests network:
    aria page 0 summarize "Is there any indication of network errors or missing resources on this page?"
    # 4. If it suggests form issues:
    aria page 0 summarize "Are there any obvious HTML form validation errors or missing input fields?"
    ```
*   **Expected Results**: Iterative analysis and suggestions from `aria` to help pinpoint the root cause of the problem.
*   **Tips / Variations**:
    *   Combine with manual inspection and developer tools in the browser.

### 7. Competitor Feature Comparison

*   **Goal**: Research features of several competitor products and compile a comparison table.
*   **Commands**:
    ```bash
    # 1. Open Competitor A's product page
    aria page new --url="https://competitorA.com/product"
    # 2. Open Competitor B's product page
    aria page new --url="https://competitorB.com/product"
    # 3. Open Competitor C's product page
    aria page new --url="https://competitorC.com/product"
    # 4. List pages for IDs
    aria page list
    # 5. Summarize key features for each
    aria page 0 summarize "List main features and pricing for Competitor A's product."
    aria page 1 summarize "List main features and pricing for Competitor B's product."
    aria page 2 summarize "List main features and pricing for Competitor C's product."
    # 6. Open a new tab and request a comparison table
    aria page new --prompt="Create a detailed comparison table of features, pricing, and unique selling points for Competitor A (tab 0), Competitor B (tab 1), and Competitor C (tab 2)."
    ```
*   **Expected Results**: Individual summaries of features/pricing, followed by a structured comparison table in a new tab.
*   **Tips / Variations**:
    *   Specify the exact features you want compared in the final prompt.

### 8. Generate a TL;DR for a Long Article

*   **Goal**: Get a very brief summary ("Too Long; Didn't Read") of a lengthy article.
*   **Commands**:
    ```bash
    # 1. Open the long article
    aria page new --url="https://very-long-article.com/about-quantum-physics"
    # 2. Summarize with a specific TL;DR instruction
    aria page 0 summarize "Provide a TL;DR (Too Long; Didn't Read) summary of this article in 3 sentences or less."
    ```
*   **Expected Results**: A very concise summary of the article.
*   **Tips / Variations**:
    *   Adjust the sentence limit in the prompt as needed.

### 9. Price Tracking for a Specific Item

*   **Goal**: Monitor the price of an item on an e-commerce site.
*   **Commands**:
    ```bash
    # This is a script candidate
    # aria script new --prompt="open product page for 'Wireless Earbuds X', extract current price, and compare it to previous recorded price (if any)."
    # (Assume this is script 0)

    # 1. Open the browser
    aria open chrome
    # 2. Run the price tracking script
    aria script 0 run
    # 3. If needed, manually inspect the page or ask for further action
    aria page 0 summarize "Has the price changed? If so, by how much?"
    ```
*   **Expected Results**: The product page is opened, and `aria` reports on the current price and any changes.
*   **Tips / Variations**:
    *   Integrate with external tools for price history logging.

### 10. Multi-Step Research and Documentation

*   **Goal**: Research a technical concept, find code examples, and then summarize for internal documentation.
*   **Commands**:
    ```bash
    # 1. Research the concept
    aria page new --prompt="explain RESTful API design principles"
    # 2. Find code examples
    aria page new --prompt="python flask restful api example"
    # 3. List pages (e.g., concept=0, examples=1)
    aria page list
    # 4. Open a new tab to create documentation draft
    aria page new --prompt="Draft a technical documentation section on 'RESTful API Design with Python Flask' using information from tab 0 (principles) and tab 1 (examples). Include key definitions, best practices, and a simple code snippet."
    ```
*   **Expected Results**: A draft of technical documentation, combining information from multiple research sources.
*   **Tips / Variations**:
    *   Specify output format (e.g., "in Markdown format").

*   **Heuristic caution**: Prompts can be ambiguous; `aria` interprets them to the best of its ability. Tab numbers can change. Local pages are temporary. Always validate results in the browser.
