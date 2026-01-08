import argparse
import os
import google.generativeai as genai
from navigator import AriaNavigator
from script_manager import ScriptManager

def summarize_text(text: str) -> str:
    """Summarizes the given text using the Gemini API."""
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Error: GEMINI_API_KEY environment variable not set."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"Summarize the following text:\n\n{text}")
        return response.text
    except Exception as e:
        return f"Error during summarization: {e}"

def main():
    parser = argparse.ArgumentParser(description="Aria CLI - Your web automation assistant.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Define the 'open' command
    parser_open = subparsers.add_parser('open', help='Open a URL in a new browser window.')
    parser_open.add_argument('url', type=str, help='The URL to navigate to.')
    parser_open.add_argument('--headless', action='store_true', help='Run the browser in headless mode.')
    parser_open.add_argument('--browser', type=str, default='chrome', choices=['chrome', 'firefox', 'edge'], help='The browser to use.')
    parser_open.add_argument('--scope', type=str, default='web', choices=['web', 'bookmarks', 'local'], help='The scope of the resource to open.')

    # Define the 'close' command
    subparsers.add_parser('close', help='Close the browser window.')

    # Define the 'page' command
    parser_page = subparsers.add_parser('page', help='Manage browser pages.')
    page_subparsers = parser_page.add_subparsers(dest="page_command", required=True)
    parser_page_new = page_subparsers.add_parser('new', help='Navigate to a new URL.')
    parser_page_new.add_argument('url', type=str, help='The URL to navigate to.')
    page_subparsers.add_parser('list', help='List all open pages.')
    parser_page_goto = page_subparsers.add_parser('goto', help='Go to a specific page.')
    parser_page_goto.add_argument('identifier', type=str, help='The 1-based index or title of the page to go to.')
    page_subparsers.add_parser('summarize', help='Summarize the current page.')

    # Define the 'script' command
    parser_script = subparsers.add_parser('script', help='Manage automation scripts.')
    script_subparsers = parser_script.add_subparsers(dest="script_command", required=True)
    parser_script_new = script_subparsers.add_parser('new', help='Create a new script.')
    parser_script_new.add_argument('name', type=str, help='The name of the script to create.')
    script_subparsers.add_parser('list', help='List all available scripts.')


    args = parser.parse_args()

    navigator = AriaNavigator()
    script_manager = ScriptManager()

    if args.command == 'open':
        if args.scope == 'web':
            if navigator.start_session(browser_name=args.browser, headless=args.headless):
                navigator.navigate(args.url)
        else:
            print(f"Scope '{args.scope}' is not yet implemented.")
    elif args.command == 'close':
        navigator.close_session()
    elif args.command == 'page':
        if args.page_command == 'new':
            navigator.navigate(args.url)
        elif args.page_command == 'list':
            tabs = navigator.list_tabs()
            if tabs:
                for i, tab in enumerate(tabs):
                    print(f"{i+1}: {tab['title']} - {tab['url']}")
            else:
                print("No active session or no open tabs found.")
        elif args.page_command == 'goto':
            identifier = args.identifier
            try:
                # Try to convert to int for index-based navigation
                identifier = int(identifier)
            except ValueError:
                # Keep as string for title-based navigation
                pass
            
            if navigator.goto_tab(identifier):
                print(f"Switched to page '{identifier}'.")
            else:
                print(f"Could not go to page '{identifier}'.")
        elif args.page_command == 'summarize':
            content = navigator.get_page_content()
            if content:
                summary = summarize_text(content)
                print(summary)
            else:
                print("Could not retrieve content from the page.")
    elif args.command == 'script':
        if args.script_command == 'new':
            script_path = script_manager.create_script(args.name)
            if script_path:
                print(f"Created new script: {script_path}")
        elif args.script_command == 'list':
            scripts = script_manager.list_scripts()
            if scripts:
                print("Available scripts:")
                for script in scripts:
                    print(f"- {script}")
            else:
                print("No scripts found.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()