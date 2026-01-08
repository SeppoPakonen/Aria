# 20-scripts.md

`aria` allows you to define and manage reusable scripts. These scripts are essentially saved prompts or sequences of actions that `aria` can execute. This runbook covers the lifecycle of `aria` scripts.

## Script Lifecycle: New, List, View, Edit, Remove

### Create a New Script (`aria script new`)

Creates a new script from a prompt. `aria` will store this prompt and assign an ID.

```bash
# Linux/macOS: Create a script to open Hacker News and summarize top topics
aria script new --prompt="open hackernews website and summarize recently most interesting topics"

# Windows CMD: Create a script to search for specific product reviews
aria script new --prompt="search amazon for 'ergonomic keyboard reviews' and list pros/cons"
```

### List All Scripts (`aria script list`)

Shows all saved scripts with their IDs and the associated prompts.

```bash
# Linux/macOS & Windows CMD
aria script list
```

### View a Specific Script (`aria script <id>`)

Displays the prompt associated with a given script ID.

```bash
# Linux/macOS & Windows CMD: View script with ID 0
aria script 0
```

### Edit an Existing Script (`aria script <id> edit`)

Modifies the prompt of an existing script. This is crucial for iteratively refining script behavior.

```bash
# Linux/macOS: Rewrite script 0 to search eBay for lawnmowers under 200 EUR in Europe
aria script 0 edit --prompt="rewrite script: make it search in ebay for lawnmowers under 200 eur in europe. then list pages locally cleanly"

# Windows CMD: Refine script 1 to include specific date ranges for reviews
aria script 1 edit --prompt="search amazon for 'ergonomic keyboard reviews from 2023-2024' and list pros/cons"
```

### Remove a Script (`aria script <id> remove`)

Deletes a script by its ID.

```bash
# Linux/macOS & Windows CMD: Remove script with ID 0
aria script 0 remove
```

## Iteratively Refine a Script with Edits

The `edit` command is powerful for developing effective `aria` scripts. You can start with a general idea and then refine it based on `aria`'s responses.

**Example Workflow:**

1.  **Initial Script**:
    ```bash
    aria script new --prompt="find popular restaurants in my city"
    # Assume this creates script with ID 0
    ```
2.  **Run and Review**: Execute the script and see what `aria` produces. If the results are too broad:
    ```bash
    aria script 0 # (to view current prompt)
    # Then manually check the browser output
    ```
3.  **Refine (Edit)**: Add more specific criteria.
    ```bash
    aria script 0 edit --prompt="find popular Italian restaurants in my city with outdoor seating and good ratings"
    ```
4.  **Repeat**: Continue running and refining until the script consistently delivers the desired output.

## Example Script Prompts for Different Domains

Here are various prompts that can be saved as `aria` scripts for different use cases.

*   **News Triage**:
    ```bash
    aria script new --prompt="open top 5 headlines from BBC News, CNN, and Al Jazeera, then summarize key geopolitical events"
    ```
*   **Shopping Research**:
    ```bash
    aria script new --prompt="compare prices and features for 'Robot Vacuum Cleaner Model X' across Amazon, Best Buy, and Walmart. List pros and cons from customer reviews."
    ```
*   **Documentation Extraction**:
    ```bash
    aria script new --prompt="navigate to 'React hooks documentation' and extract examples for 'useState' and 'useEffect' with code snippets."
    ```
*   **Job Search**:
    ```bash
    aria script new --prompt="search LinkedIn and Indeed for 'Senior Software Engineer' roles in New York, filtering for remote options and positions posted in the last week. List job titles, companies, and key requirements."
    ```
*   **Travel Planning**:
    ```bash
    aria script new --prompt="plan a 7-day trip to Kyoto, Japan, in spring. Suggest itinerary including cultural sites, food experiences, and budget-friendly accommodation options."
    ```
*   **Security Hygiene**:
    ```bash
    aria script new --prompt="check if my email address is part of any known data breaches using 'Have I Been Pwned?' and report findings."
    ```
*   **File Cleanup**:
    ```bash
    aria script new --prompt="list all temporary files older than 30 days in my Downloads folder and suggest which can be safely deleted."
    ```
*   **Compare Vendors**:
    ```bash
    aria script new --prompt="research cloud providers (AWS, Azure, GCP) for serverless functions pricing and feature comparison. Generate a table of findings."
    ```

## Design Patterns

To get the most out of `aria` scripts, consider these design patterns:

*   **Keep Prompts Specific**: Vague prompts lead to vague results. Be as explicit as possible about what you want `aria` to do.
*   **Request Structured Output**: If you need data in a particular format (e.g., a list, a table, pros/cons), explicitly ask for it in your prompt.
*   **Ask it to Open Local Pages for Results**: For tasks involving data extraction or comparison, instruct `aria` to generate a `local` scope page. This provides a temporary, viewable summary that you can then interact with further.

## Safety and Compliance Notes

*   **Do Not Automate Logins That Violate Terms**: Avoid creating scripts that automatically log into services if doing so violates their terms of service, especially if it bypasses security measures.
*   **Keep User in the Loop for 2FA/Captcha**: For any sensitive operations requiring two-factor authentication (2FA) or CAPTCHA, design your scripts to pause or alert you, allowing for manual intervention. `aria` is a powerful tool; use it responsibly.
*   **Heuristic Caution**: Prompts can be ambiguous; `aria` interprets them to the best of its ability. Always validate results in the browser.
