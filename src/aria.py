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
    
    parser_page_new = page_subparsers.add_parser('new', help='Create a new page.')
    parser_page_new.add_argument('url', type=str, nargs='?', help='The URL to navigate to.')
    parser_page_new.add_argument('--url', type=str, dest='url_opt', help='The URL to navigate to.')
    parser_page_new.add_argument('--prompt', type=str, help='Prompt to generate content (not fully implemented).')
    parser_page_new.add_argument('--scope', type=str, default='web', choices=['web', 'local'], help='Scope for the new page.')

    page_subparsers.add_parser('list', help='List all open pages.')
    
    parser_page_goto = page_subparsers.add_parser('goto', help='Go to a specific page or navigate it.')
    parser_page_goto.add_argument('identifier', type=str, nargs='?', help='The 1-based index, ID or title of the page.')
    parser_page_goto.add_argument('--url', type=str, help='Navigate the tab to this URL.')
    parser_page_goto.add_argument('--prompt', type=str, help='Navigate using a prompt (not fully implemented).')

    parser_page_summarize = page_subparsers.add_parser('summarize', help='Summarize a page.')
    parser_page_summarize.add_argument('identifier', type=str, nargs='?', help='The 1-based index, ID or title of the page.')
    parser_page_summarize.add_argument('prompt', type=str, nargs='?', help='Specific instructions for summarization.')

    # Define the 'script' command
    parser_script = subparsers.add_parser('script', help='Manage automation scripts.')
    script_subparsers = parser_script.add_subparsers(dest="script_command", required=True)
    parser_script_new = script_subparsers.add_parser('new', help='Create a new script.')
    parser_script_new.add_argument('name', type=str, help='The name of the script to create.')
    script_subparsers.add_parser('list', help='List all available scripts.')
    parser_script_edit = script_subparsers.add_parser('edit', help='Edit an existing script.')
    parser_script_edit.add_argument('name', type=str, help='The name of the script to edit.')
    parser_script_remove = script_subparsers.add_parser('remove', help='Remove a script.')
    parser_script_remove.add_argument('name', type=str, help='The name of the script to remove.')
    parser_script_remove.add_argument('--force', action='store_true', help='Remove without confirmation.')
    parser_script_run = script_subparsers.add_parser('run', help='Run a script.')
    parser_script_run.add_argument('name', type=str, help='The name of the script to run.')

    # Define the 'diag' command
    subparsers.add_parser('diag', help='Show diagnostic information.')

    args = parser.parse_args()
    logger.info(f"Command received: {args.command}")

    navigator = AriaNavigator()
    script_manager = ScriptManager()
    safety_manager = SafetyManager()

    if args.command == 'open':
        safety_manager.ensure_disclaimer_accepted()
        if args.scope == 'web':
            force = False
            if os.path.exists(navigator.get_session_file_path()):
                if navigator.connect_to_session():
                    if safety_manager.confirm("An Aria session is already active. Do you want to restart it?", default=False):
                        force = True
                    else:
                        print("Aborted.")
                        return

            if navigator.start_session(browser_name=args.browser, headless=args.headless, force=force):
                navigator.navigate(args.url)
        else:
            print(f"Scope '{args.scope}' is not yet implemented.")
    elif args.command == 'close':
        navigator.close_session()
    elif args.command == 'page':
        if args.page_command == 'new':
            url = args.url_opt or args.url
            if url:
                navigator.navigate(url)
                print(f"Successfully navigated to {url}")
            elif args.prompt:
                print(f"Prompt-based page creation ('{args.prompt}') is not yet fully implemented.")
            else:
                print("Error: URL or prompt required for 'page new'.")
        elif args.page_command == 'list':
            tabs = navigator.list_tabs()
            if tabs:
                print("Open pages:")
                for i, tab in enumerate(tabs):
                    # In a real implementation, we'd show the session-specific ID too
                    print(f"{i+1}: {tab['title']} - {tab['url']}")
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
            
            if args.url:
                navigator.navigate(args.url)
            elif args.prompt:
                print(f"Prompt-based navigation ('{args.prompt}') is not yet fully implemented.")
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
        elif args.script_command == 'edit':
            script_path = script_manager.get_script_path(args.name)
            if script_path:
                print(f"Opening script for editing: {script_path}")
                try:
                    os.startfile(script_path)
                except AttributeError:
                    # For non-Windows platforms (future)
                    import subprocess
                    import sys
                    if sys.platform == "darwin":
                        subprocess.run(["open", script_path])
                    else:
                        subprocess.run(["xdg-open", script_path])
            else:
                print(f"Error: Script '{args.name}' not found.")
        elif args.script_command == 'remove':
            if not args.force:
                if not safety_manager.confirm(f"Are you sure you want to remove script '{args.name}'?"):
                    print("Aborted.")
                    return
            
            if script_manager.remove_script(args.name):
                print(f"Script '{args.name}' removed successfully.")
            else:
                print(f"Error: Script '{args.name}' not found or could not be removed.")
        elif args.script_command == 'run':
            safety_manager.ensure_disclaimer_accepted()
            script_manager.run_script(args.name)
    elif args.command == 'diag':
        import sys
        import platform
        print(f"Aria Version: {VERSION}")
        print(f"Python Version: {sys.version}")
        print(f"Platform: {platform.platform()}")
        
        aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
        print(f"Aria Directory: {aria_dir}")
        
        session_file = navigator.get_session_file_path()
        if os.path.exists(session_file):
            print(f"Active Session: Found (File: {session_file})")
            if navigator.connect_to_session():
                print("Session Status: Live")
            else:
                print("Session Status: Stale/Dead")
        else:
            print("Active Session: None")
            
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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()