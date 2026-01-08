import argparse
import os
import google.generativeai as genai
from navigator import AriaNavigator
from script_manager import ScriptManager
from safety_manager import SafetyManager
from logger import setup_logging, get_logger

logger = get_logger("aria")

VERSION = "0.1.0"

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
    setup_logging()
    
    # Pre-process sys.argv for 'page' command to support 'aria page <id> <cmd>'
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == 'page':
        if sys.argv[2] not in ['new', 'list', 'goto', 'summarize', '-h', '--help']:
            # Assume sys.argv[2] is an identifier
            # If sys.argv[3] is 'goto' or 'summarize', swap them
            if len(sys.argv) > 3 and sys.argv[3] in ['goto', 'summarize']:
                ident = sys.argv.pop(2)
                sys.argv.insert(3, ident)

    # Pre-process sys.argv for 'script' command to support 'aria script <id> <cmd>'
    if len(sys.argv) > 2 and sys.argv[1] == 'script':
        if sys.argv[2] not in ['new', 'list', 'edit', 'remove', 'run', '-h', '--help']:
            # Assume sys.argv[2] is an identifier
            if len(sys.argv) > 3 and sys.argv[3] in ['edit', 'remove', 'run']:
                ident = sys.argv.pop(2)
                sys.argv.insert(3, ident)
            else:
                # 'aria script <id>' - just viewing
                # We'll treat this as 'aria script view <id>' internally
                ident = sys.argv.pop(2)
                sys.argv.insert(2, 'view')
                sys.argv.insert(3, ident)

    parser = argparse.ArgumentParser(description="Aria CLI - Your web automation assistant.")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Define the 'open' command
    parser_open = subparsers.add_parser('open', help='Open a browser instance.')
    parser_open.add_argument('url', type=str, nargs='?', help='Optional URL to navigate to.')
    parser_open.add_argument('--headless', action='store_true', help='Run the browser in headless mode.')
    parser_open.add_argument('--browser', type=str, default='chrome', choices=['chrome', 'firefox', 'edge'], help='The browser to use.')
    parser_open.add_argument('--scope', type=str, default='web', choices=['web', 'bookmarks', 'local'], help='The scope of the resource to open.')

    # Define the 'close' command
    parser_close = subparsers.add_parser('close', help='Close browser instances.')
    parser_close.add_argument('browser', type=str, nargs='?', choices=['chrome', 'firefox', 'edge'], help='The browser to close. If omitted, closes all.')

    # Define the 'page' command
    parser_page = subparsers.add_parser('page', help='Manage browser pages.')
    page_subparsers = parser_page.add_subparsers(dest="page_command", required=True)
    
    parser_page_new = page_subparsers.add_parser('new', help='Create a new page.')
    parser_page_new.add_argument('url', type=str, nargs='?', help='The URL to navigate to.')
    parser_page_new.add_argument('--url', type=str, dest='url_opt', help='The URL to navigate to.')
    parser_page_new.add_argument('--prompt', type=str, help='Prompt to generate content (not fully implemented).')
    parser_page_new.add_argument('--scope', type=str, default='web', choices=['web', 'local'], help='Scope for the new page.')

    page_subparsers.add_parser('list', help='List all open pages.')
    
    parser_page_goto = page_subparsers.add_parser('goto', help='Go to a specific page or navigate it.')
    parser_page_goto.add_argument('identifier', type=str, nargs='?', help='The index (0-based), ID or title of the page.')
    parser_page_goto.add_argument('--url', type=str, help='Navigate the tab to this URL.')
    parser_page_goto.add_argument('--prompt', type=str, help='Navigate using a prompt (not fully implemented).')
    parser_page_goto.add_argument('--scope', type=str, default='web', choices=['web', 'bookmarks'], help='Scope for navigation.')

    parser_page_summarize = page_subparsers.add_parser('summarize', help='Summarize a page.')
    parser_page_summarize.add_argument('identifier', type=str, nargs='?', help='The index (0-based), ID or title of the page.')
    parser_page_summarize.add_argument('prompt', type=str, nargs='?', help='Specific instructions for summarization.')

    # Define the 'script' command
    parser_script = subparsers.add_parser('script', help='Manage automation scripts.')
    script_subparsers = parser_script.add_subparsers(dest="script_command", required=True)
    
    parser_script_new = script_subparsers.add_parser('new', help='Create a new script.')
    parser_script_new.add_argument('--prompt', type=str, required=True, help='The prompt for the script.')
    parser_script_new.add_argument('--name', type=str, help='Optional name for the script.')
    
    script_subparsers.add_parser('list', help='List all available scripts.')
    
    parser_script_view = script_subparsers.add_parser('view', help='View a script prompt.')
    parser_script_view.add_argument('identifier', type=str, help='The ID or name of the script.')

    parser_script_edit = script_subparsers.add_parser('edit', help='Edit an existing script.')
    parser_script_edit.add_argument('identifier', type=str, help='The ID or name of the script to edit.')
    parser_script_edit.add_argument('--prompt', type=str, required=True, help='The new prompt for the script.')
    
    parser_script_remove = script_subparsers.add_parser('remove', help='Remove a script.')
    parser_script_remove.add_argument('identifier', type=str, help='The ID or name of the script to remove.')
    parser_script_remove.add_argument('--force', action='store_true', help='Remove without confirmation.')
    
    parser_script_run = script_subparsers.add_parser('run', help='Run a script.')
    parser_script_run.add_argument('identifier', type=str, help='The ID or name of the script to run.')

    # Define the 'diag' command
    subparsers.add_parser('diag', help='Show diagnostic information.')

    # Define the 'settings' command
    subparsers.add_parser('settings', help='Show current configuration.')

    # Define the 'man' command
    subparsers.add_parser('man', help='Show manual pages.')

    # Define the 'tutorial' command
    subparsers.add_parser('tutorial', help='Start the interactive tutorial.')

    # Define the 'version' command
    subparsers.add_parser('version', help='Show version information.')

    args = parser.parse_args()
    logger.info(f"Command received: {args.command}")

    navigator = AriaNavigator()
    script_manager = ScriptManager()
    safety_manager = SafetyManager()

    if args.command == 'open':
        safety_manager.ensure_disclaimer_accepted()
        
        # Check if we should use the positional 'url' or treat it as a browser name if it was 'aria open firefox'
        # But 'browser' is a flag. Wait, the runbook says 'aria open firefox'.
        # My parser has 'url' as positional.
        
        browser_to_open = args.browser
        url_to_navigate = args.url
        
        # Heuristic: if 'url' matches a browser name, maybe user meant browser?
        if args.url in ['chrome', 'firefox', 'edge']:
            browser_to_open = args.url
            url_to_navigate = None

        if args.scope == 'web':
            if navigator.start_session(browser_name=browser_to_open, headless=args.headless):
                if url_to_navigate:
                    navigator.navigate(url_to_navigate)
        else:
            print(f"Scope '{args.scope}' is not yet implemented.")
    elif args.command == 'close':
        navigator.close_session(args.browser)
    elif args.command == 'page':
        if args.page_command == 'new':
            if args.scope == 'local':
                print(f"Local scope for 'page new' ('{args.prompt}') is not yet implemented.")
                return

            url = args.url_opt or args.url
            if url:
                if navigator.new_tab(url):
                    print(f"Opened new page and navigated to {url}")
            elif args.prompt:
                if navigator.new_tab():
                    navigator.navigate_with_prompt(args.prompt)
            else:
                # Default to blank new tab if no URL/prompt
                if navigator.new_tab():
                    print("Opened a new blank page.")
        elif args.page_command == 'list':
            tabs = navigator.list_tabs()
            if tabs:
                print("Open pages:")
                for i, tab in enumerate(tabs):
                    print(f"{i}: ({tab['id'][:8]}) \"{tab['title']}\" - {tab['url']}")
            else:
                print("No active session or no open tabs found.")
        elif args.page_command == 'goto':
            if args.identifier:
                identifier = args.identifier
                try:
                    identifier = int(identifier)
                except ValueError:
                    pass
                
                if not navigator.goto_tab(identifier):
                    print(f"Error: Could not switch to page '{identifier}'.")
                    return
            
            if args.scope == 'bookmarks':
                print(f"Bookmarks scope for 'page goto' ('{args.prompt}') is not yet implemented.")
                return

            if args.url:
                navigator.navigate(args.url)
            elif args.prompt:
                navigator.navigate_with_prompt(args.prompt)
            elif args.identifier:
                print(f"Switched to page '{args.identifier}'.")
            else:
                print("Error: Identifier, URL, or prompt required for 'page goto'.")

        elif args.page_command == 'summarize':
            if args.identifier:
                identifier = args.identifier
                try:
                    identifier = int(identifier)
                except ValueError:
                    pass
                if not navigator.goto_tab(identifier):
                    print(f"Error: Could not switch to page '{identifier}'.")
                    return

            content = navigator.get_page_content()
            if content:
                prompt = args.prompt or "Summarize the following text:"
                summary = summarize_text(f"{prompt}\n\n{content}")
                print(summary)
            else:
                print("Could not retrieve content from the page.")
    elif args.command == 'script':
        if args.script_command == 'new':
            script_id = script_manager.create_script(args.prompt, args.name)
            print(f"Created new script with ID: {script_id}")
        elif args.script_command == 'list':
            scripts = script_manager.list_scripts()
            if scripts:
                print("Available scripts:")
                for s in scripts:
                    print(f"{s['id']}: {s['prompt'][:50]}...")
            else:
                print("No scripts found.")
        elif args.script_command == 'view':
            script = script_manager.get_script(args.identifier)
            if script:
                print(f"Script {script['id']} (Name: {script['name']}):")
                print(f"Prompt: {script['prompt']}")
            else:
                print(f"Error: Script '{args.identifier}' not found.")
        elif args.script_command == 'edit':
            if script_manager.edit_script(args.identifier, args.prompt):
                print(f"Script '{args.identifier}' updated successfully.")
            else:
                print(f"Error: Script '{args.identifier}' not found.")
        elif args.script_command == 'remove':
            if not args.force:
                if not safety_manager.confirm(f"Are you sure you want to remove script '{args.identifier}'?"):
                    print("Aborted.")
                    return
            
            if script_manager.remove_script(args.identifier):
                print(f"Script '{args.identifier}' removed successfully.")
            else:
                print(f"Error: Script '{args.identifier}' not found or could not be removed.")
        elif args.script_command == 'run':
            safety_manager.ensure_disclaimer_accepted()
            script_manager.run_script(args.identifier, navigator=navigator)
    elif args.command == 'diag':
        import sys
        import platform
        print(f"Aria Version: {VERSION}")
        print(f"Python Version: {sys.version}")
        print(f"Platform: {platform.platform()}")
        
        aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
        print(f"Aria Directory: {aria_dir}")
        
        browsers = navigator.list_active_browsers()
        if browsers:
            print(f"Active Sessions: {', '.join(browsers)}")
        else:
            print("Active Sessions: None")
            
        log_file = os.path.join(aria_dir, "aria.log")
        if os.path.exists(log_file):
            print("\nRecent Logs (last 10 lines):")
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:
                        print(line.strip())
            except Exception as e:
                print(f"Error reading log file: {e}")
        else:
            print("\nLog file not found.")
    elif args.command == 'settings':
        aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
        print(f"Aria Configuration:")
        print(f"  Aria Home: {aria_dir}")
        print(f"  Scripts Directory: {os.path.join(aria_dir, 'scripts')}")
        print(f"  Current Browser: {navigator._get_current_browser()}")
        print(f"  Active Browsers: {', '.join(navigator.list_active_browsers())}")
    elif args.command == 'man':
        print("Aria Manual Pages")
        print("================")
        print("\nAria is an AI-driven web automation assistant.")
        print("\nCommands:")
        print("  open [browser]   - Start a browser session.")
        print("  close [browser]  - Close browser session(s).")
        print("  page list        - List open tabs.")
        print("  page new --url U - Open a new tab.")
        print("  page <id> goto   - Navigate a tab.")
        print("  script list      - List saved scripts.")
        print("  script run <id>  - Execute a saved script.")
        print("\nSee runbooks in docs/runbooks/ for full details.")
    elif args.command == 'tutorial':
        print("Welcome to the Aria Tutorial!")
        print("1. Start by opening a browser: 'aria open chrome'")
        print("2. Navigate to a site: 'aria page new --url https://google.com'")
        print("3. List your tabs: 'aria page list'")
        print("4. Summarize a page: 'aria page 0 summarize'")
        print("5. Create a script: 'aria script new --prompt \"my search\"'")
        print("\nHappy automating!")
    elif args.command == 'version':
        print(f"aria CLI version {VERSION}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()