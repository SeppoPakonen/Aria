#!/bin/bash
# Example script for running Aria in a non-interactive CI environment

# 1. Start a headless browser session
echo "Starting headless browser session..."
python3 src/aria.py open --headless --browser chrome

# 2. Run an automation script (assumes ID 0 exists or use name)
# Use --force to bypass any safety confirmations
echo "Running automation script..."
python3 src/aria.py --force script run 0

# 3. Summarize the result and generate a report
echo "Generating summary report..."
python3 src/aria.py page 0 summarize "Check for any errors on the page" --report --report-format markdown

# 4. Cleanup
echo "Closing browser session..."
python3 src/aria.py close

echo "CI run complete. Check ~/.aria/reports for artifacts."
