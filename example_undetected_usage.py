#!/usr/bin/env python3
"""
Example script showing how to use undetected geckodriver as requested.
This provides the exact functionality you wanted while keeping the Aria framework stable.
"""

# Example usage as requested:
from undetected_geckodriver import Firefox

# Create a Firefox instance with undetected capabilities
driver = Firefox()

# Navigate to a website
driver.get("https://www.example.com")

# Print the title to confirm it worked
print(f"Page title: {driver.title}")

# Close the browser when done
driver.quit()

print("Successfully used undetected geckodriver!")