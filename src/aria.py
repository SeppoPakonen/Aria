import argparse
import os
import google.generativeai as genai
import re
import logging
from navigator import AriaNavigator
from script_manager import ScriptManager
from safety_manager import SafetyManager
from plugin_manager import PluginManager
from logger import setup_logging, get_logger, set_trace_id, time_it, get_performance_metrics
from report_manager import ReportManager
from exceptions import AriaError

logger = get_logger("aria")

VERSION = "0.1.0"

@time_it(logger)
def generate_ai_response(prompt: str, context: str = "", output_format: str = "text", plugin_manager: PluginManager = None) -> str:
    """Generates a response from the AI given a prompt and optional context."""
    if plugin_manager:
        plugin_manager.trigger_hook("pre_ai_generation", prompt=prompt)

    logger.info(f"Generating AI response. Format: {output_format}", extra={"prompt_length": len(prompt), "context_length": len(context)})
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable not set.")
            return "Error: GEMINI_API_KEY environment variable not set."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nUser Request: {prompt}"
        
        if output_format == "json":
            full_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. Do not include markdown code blocks or any other text."
        elif output_format == "markdown":
            full_prompt += "\n\nIMPORTANT: Use Markdown formatting."
        
        response = model.generate_content(full_prompt)
        text = response.text
        
        logger.info("AI response generated successfully.", extra={"response_length": len(text)})
        
        # Simple cleanup if AI includes markdown code blocks
        if output_format == "json" and text.startswith("```json"):
            text = text.replace("```json", "", 1).replace("```", "", 1).strip()
        elif output_format == "json" and text.startswith("```"):
            text = text.replace("```", "", 1).replace("```", "", 1).strip()
            
        if plugin_manager:
            plugin_manager.trigger_hook("post_ai_generation", prompt=prompt, response=text)

        return text
    except Exception as e:
        logger.error(f"Error during AI generation: {e}", exc_info=True)
        return f"Error during AI generation: {e}"

def summarize_text(text: str, output_format: str = "text", plugin_manager: PluginManager = None) -> str:
    """Summarizes the given text using the Gemini API."""
    prompt = "Summarize the following text:"
    if output_format == "json":
        prompt = "Summarize the following text and return it as valid JSON with keys 'summary', 'key_points' (list), and 'overall_sentiment':"
    return generate_ai_response(prompt, text, output_format=output_format, plugin_manager=plugin_manager)

def safe_navigate(url, navigator, safety_manager, force=False):
    """Navigates to a URL only if it passes the safety check."""
    if safety_manager.check_url_safety(url, force=force):
        navigator.navigate(url)
        return True
    return False

def safe_new_tab(url, navigator, safety_manager, force=False):
    """Opens a new tab with a URL only if it passes the safety check."""
    if safety_manager.check_url_safety(url, force=force):
        return navigator.new_tab(url)
    return False

def main():
    try:
        _run_cli()
    except AriaError as e:
        print(f"Error: {e}")
        logger.error(f"AriaError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)

def _run_cli():
    # Pre-process sys.argv for 'page' command to support 'aria page <id> <cmd>'
    import sys
    
    # Initialize core managers early to provide context to plugins
    navigator = AriaNavigator()
    script_manager = ScriptManager()
    safety_manager = SafetyManager()
    report_manager = ReportManager()

    plugin_manager = PluginManager(context={
        "navigator": navigator,
        "script_manager": script_manager,
        "safety_manager": safety_manager,
        "report_manager": report_manager,
        "version": VERSION
    })
    
    # Give navigator access to plugin manager for hooks
    navigator.plugin_manager = plugin_manager
    
    plugin_manager.load_plugins()

    if len(sys.argv) > 2 and sys.argv[1] == 'page':
        if sys.argv[2] not in ['new', 'list', 'goto', 'summarize', 'tag', 'export', '-h', '--help']:
            # Assume sys.argv[2] is an identifier
            # If sys.argv[3] is 'goto', 'summarize', 'tag', or 'export', swap them
            if len(sys.argv) > 3 and sys.argv[3] in ['goto', 'summarize', 'tag', 'export']:
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
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level.')
    parser.add_argument('--json-logs', action='store_true', help='Use JSON format for file logging.')
    parser.add_argument('--trace-id', type=str, help='Optional trace ID for this execution.')
    parser.add_argument('--force', action='store_true', help='Force actions and bypass safety warnings.')
    parser.add_argument('--slow-mo', type=float, default=0.0, help='Add a delay in seconds between browser actions.')
    
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
    parser_page_new.add_argument('--format', type=str, choices=['text', 'json', 'markdown'], default='text', help='Output format for prompt generation.')

    page_subparsers.add_parser('list', help='List all open pages.')
    
    parser_page_goto = page_subparsers.add_parser('goto', help='Go to a specific page or navigate it.')
    parser_page_goto.add_argument('identifier', type=str, nargs='?', help='The index (0-based), ID or title of the page.')
    parser_page_goto.add_argument('--url', type=str, help='Navigate the tab to this URL.')
    parser_page_goto.add_argument('--prompt', type=str, help='Navigate using a prompt (not fully implemented).')
    parser_page_goto.add_argument('--scope', type=str, default='web', choices=['web', 'bookmarks'], help='Scope for navigation.')

    parser_page_summarize = page_subparsers.add_parser('summarize', help='Summarize a page.')
    parser_page_summarize.add_argument('identifier', type=str, nargs='?', help='The index (0-based), ID or title of the page.')
    parser_page_summarize.add_argument('prompt', type=str, nargs='?', help='Specific instructions for summarization.')
    parser_page_summarize.add_argument('--format', type=str, choices=['text', 'json', 'markdown'], default='text', help='Output format for the summary.')
    parser_page_summarize.add_argument('--report', action='store_true', help='Generate a local report file for the summary.')
    parser_page_summarize.add_argument('--report-format', type=str, choices=['markdown', 'html'], default='markdown', help='Format of the generated report.')

    parser_page_tag = page_subparsers.add_parser('tag', help='Tag a page.')
    parser_page_tag.add_argument('identifier', type=str, help='The index, ID or title of the page.')
    parser_page_tag.add_argument('tag', type=str, help='The tag to add.')

    parser_page_export = page_subparsers.add_parser('export', help='Export page content to a file.')
    parser_page_export.add_argument('identifier', type=str, nargs='?', help='The index, ID or title of the page.')
    parser_page_export.add_argument('--path', type=str, help='Optional path to save the report.')
    parser_page_export.add_argument('--format', type=str, choices=['markdown', 'html'], default='markdown', help='Format of the exported file.')

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
    parser_script_run.add_argument('--param', action='append', help='Parameters for the script in name=value format.')

    # Define the 'report' command
    parser_report = subparsers.add_parser('report', help='Manage local reports.')
    report_subparsers = parser_report.add_subparsers(dest="report_command", required=True)
    
    parser_report_generate = report_subparsers.add_parser('generate', help='Generate a report from a prompt.')
    parser_report_generate.add_argument('prompt', type=str, help='The prompt to generate report content.')
    parser_report_generate.add_argument('--title', type=str, help='Title for the report.')
    parser_report_generate.add_argument('--format', type=str, choices=['markdown', 'html'], default='markdown', help='Format of the generated report.')
    
    report_subparsers.add_parser('list', help='List all generated reports.')

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

    # Define the 'security' command
    subparsers.add_parser('security', help='Show security best practices.')

    # Add plugin commands
    plugin_commands = plugin_manager.get_plugin_commands()
    for cmd_def in plugin_commands:
        p = subparsers.add_parser(cmd_def['name'], help=cmd_def.get('help'))
        for arg in cmd_def.get('arguments', []):
            arg_copy = arg.copy()
            name = arg_copy.pop('name')
            p.add_argument(name, **arg_copy)
        p.set_defaults(func=cmd_def['callback'])

    args = parser.parse_args()
    
    # Set unique trace ID for this command execution
    trace_id = set_trace_id(args.trace_id)
    
    # Configure logging based on args
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    setup_logging(level=log_level, json_format=args.json_logs)
    
    logger.info(f"Command received: {args.command}", extra={"command": args.command, "arguments": vars(args)})

    # Dispatch to plugin command if applicable
    if hasattr(args, 'func'):
        args.func(args)
        return

    # Auto-detect format from prompt for certain commands
    if args.command == 'page' and args.page_command in ['new', 'summarize']:
        if hasattr(args, 'format') and args.format == 'text':
            prompt_text = (args.prompt or "").lower()
            if "json" in prompt_text:
                args.format = "json"
            elif "table" in prompt_text or "markdown" in prompt_text:
                args.format = "markdown"

    if args.slow_mo > 0:
        navigator.throttle_delay = args.slow_mo
        
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
                    safe_navigate(url_to_navigate, navigator, safety_manager, force=args.force)
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
                if safe_new_tab(url, navigator, safety_manager, force=args.force):
                    print(f"Opened new page and navigated to {url}")
            elif args.prompt:
                # Check for cross-tab synthesis
                refined_prompt, context = navigator.resolve_prompt(args.prompt)
                if context:
                    print("Synthesizing information across tabs...")
                    result = generate_ai_response(refined_prompt, context, output_format=args.format, plugin_manager=plugin_manager)
                    print(result)
                else:
                    if safety_manager.check_url_safety(args.prompt, force=args.force):
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
                    tag_str = f" [tags: {', '.join(tab['tags'])}]" if tab.get('tags') else ""
                    print(f"{i}: ({tab['id'][:8]}) \"{tab['title']}\" - {tab['url']}{tag_str}")
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
                safe_navigate(args.url, navigator, safety_manager, force=args.force)
            elif args.prompt:
                if safety_manager.check_url_safety(args.prompt, force=args.force):
                    navigator.navigate_with_prompt(args.prompt)
            elif args.identifier:
                print(f"Switched to page '{args.identifier}'.")
            else:
                print("Error: Identifier, URL, or prompt required for 'page goto'.")

        elif args.page_command == 'tag':
            if not navigator.tag_tab(args.identifier, args.tag):
                print(f"Error: Could not tag page '{args.identifier}'.")

        elif args.page_command == 'export':
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
                url = navigator.get_current_url()
                title = navigator._driver.title if navigator._driver else "Exported Page"
                reports_dir = os.path.dirname(args.path) if args.path else None
                
                # If path is provided, we might want to override the default reports dir
                # For now, let's just use ReportManager but maybe allow custom path
                if args.path:
                    # If path is provided, we use the specified path and extension
                    with open(args.path, "w", encoding="utf-8") as f:
                        if args.path.endswith(".html"):
                            # Minimal HTML if direct path is used but it's .html
                            f.write(f"<html><body><h1>{title}</h1><p>Source: {url}</p><pre>{content}</pre></body></html>")
                        else:
                            f.write(f"# {title}\n\n**Source:** {url}\n\n{content}")
                    path = args.path
                else:
                    metrics = get_performance_metrics()
                    if args.format == 'html':
                        path = report_manager.generate_html_report(title, content, sources=[url], metrics=metrics)
                    else:
                        path = report_manager.generate_markdown_report(title, content, sources=[url], metrics=metrics)
                
                print(f"Page exported to: {path}")
            else:
                print("Could not retrieve content from the page.")

        elif args.page_command == 'summarize':
            # Check for cross-tab synthesis in the prompt
            if args.prompt:
                refined_prompt, context = navigator.resolve_prompt(args.prompt)
                if context:
                    print("Synthesizing information across tabs for summary...")
                    result = generate_ai_response(refined_prompt, context, output_format=args.format, plugin_manager=plugin_manager)
                    print(result)
                    if args.report:
                        metrics = get_performance_metrics()
                        if args.report_format == 'html':
                            path = report_manager.generate_html_report("Summary Report", result, sources=navigator.list_active_browsers(), metrics=metrics)
                        else:
                            path = report_manager.generate_markdown_report("Summary Report", result, sources=navigator.list_active_browsers(), metrics=metrics)
                        print(f"Report generated: {path}")
                    return

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
                summary = summarize_text(f"{prompt}\n\n{content}", output_format=args.format, plugin_manager=plugin_manager)
                print(summary)
                if args.report:
                    metrics = get_performance_metrics()
                    if args.report_format == 'html':
                        path = report_manager.generate_html_report("Page Summary", summary, sources=[navigator.get_current_url()], metrics=metrics)
                    else:
                        path = report_manager.generate_markdown_report("Page Summary", summary, sources=[navigator.get_current_url()], metrics=metrics)
                    print(f"Report generated: {path}")
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
            script = script_manager.get_script(args.identifier)
            if not script:
                print(f"Error: Script '{args.identifier}' not found.")
                return

            params = {}
            if args.param:
                for p in args.param:
                    if '=' in p:
                        k, v = p.split('=', 1)
                        params[k] = v
            
            # Preview prompt with params if possible, or just check placeholders
            prompt = script['prompt']
            placeholders = script_manager.get_script_placeholders(prompt)
            if not placeholders:
                if not safety_manager.check_url_safety(prompt, force=args.force):
                    print("Aborted due to safety concerns.")
                    return
            else:
                # If there are placeholders, we might check after they are filled.
                # ScriptManager.run_script handles prompting for missing params.
                # For now, let's at least check the base prompt.
                if not safety_manager.check_url_safety(prompt, force=args.force):
                    print("Warning: Base script prompt contains sensitive keywords.")
                    if not args.force and not safety_manager.confirm("Proceed to fill parameters?"):
                        return

            script_manager.run_script(args.identifier, navigator=navigator, parameters=params)
    elif args.command == 'report':
        if args.report_command == 'generate':
            refined_prompt, context = navigator.resolve_prompt(args.prompt)
            print("Generating report content...")
            result = generate_ai_response(refined_prompt, context, plugin_manager=plugin_manager)
            title = args.title or "General Report"
            metrics = get_performance_metrics()
            if args.format == 'html':
                path = report_manager.generate_html_report(title, result, sources=navigator.list_active_browsers(), metrics=metrics)
            else:
                path = report_manager.generate_markdown_report(title, result, sources=navigator.list_active_browsers(), metrics=metrics)
            print(f"Report generated: {path}")
        elif args.report_command == 'list':
            import os
            reports_dir = report_manager.reports_dir
            if os.path.exists(reports_dir):
                files = [f for f in os.listdir(reports_dir) if f.endswith((".md", ".html"))]
                if files:
                    print("Available Reports:")
                    for f in sorted(files, reverse=True):
                        print(f"- {f}")
                else:
                    print("No reports found.")
            else:
                print("No reports found.")
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
        print(f"  Plugins Directory: {os.path.join(aria_dir, 'plugins')}")
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
        print("  security         - Show security best practices.")
        print("\nOptions:")
        print("  --slow-mo SEC    - Add delay between actions.")
        print("  --force          - Bypass safety warnings.")
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
    elif args.command == 'security':
        print(safety_manager.get_security_best_practices())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()