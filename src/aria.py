import argparse
import os
from google import genai
import re
import logging
from navigator import AriaNavigator
from script_manager import ScriptManager
from safety_manager import SafetyManager
from plugin_manager import PluginManager, BaseAIProvider
from logger import setup_logging, get_logger, set_trace_id, time_it, get_performance_metrics
from report_manager import ReportManager
from credential_manager import CredentialManager
from site_manager import SiteManager
from sites.google_messages import GoogleMessagesScraper
from sites.whatsapp import WhatsAppScraper
from sites.discord import DiscordScraper
from sites.threads import ThreadsScraper
from sites.calendar import CalendarScraper
from sites.youtube_studio import YouTubeStudioScraper
from exceptions import AriaError

logger = get_logger("aria")

VERSION = "0.1.0"

class GeminiProvider(BaseAIProvider):
    def generate(self, prompt: str, context: str = "", output_format: str = "text") -> str:
        cli_path = os.path.expanduser("~/node_modules/.bin/gemini")
        if os.path.exists(cli_path):
            return self._generate_via_cli(cli_path, prompt, context, output_format)
        
        return self._generate_via_sdk(prompt, context, output_format)

    def _generate_via_cli(self, cli_path, prompt, context, output_format):
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{context}\n\nUser Request: {prompt}"
            
            if output_format == "json":
                full_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. Do not include markdown code blocks or any other text."
            elif output_format == "markdown":
                full_prompt += "\n\nIMPORTANT: Use Markdown formatting."

            import subprocess
            import json
            
            # The user suggested: echo prompt | gemini -y -o stream-json -
            # Added --model gemini-3-flash-preview
            cmd = [cli_path, "-y", "--model", "gemini-3-flash-preview", "-o", "stream-json", "-"]
            
            process = subprocess.Popen(
                cmd, 
                stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=full_prompt)
            
            if process.returncode != 0:
                logger.error(f"Gemini CLI error: {stderr}")
                return f"Error from Gemini CLI: {stderr}"

            # Parse NDJSON output
            response_text = ""
            for line in stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if data.get("type") == "message" and data.get("role") == "assistant":
                        content = data.get("content", "")
                        response_text += content
                except json.JSONDecodeError:
                    pass

            text = response_text.strip()
            
            # Cleanup
            if output_format == "json" and text.startswith("```json"):
                text = text.replace("```json", "", 1).replace("```", "", 1).strip()
            elif output_format == "json" and text.startswith("```"):
                text = text.replace("```", "", 1).replace("```", "", 1).strip()

            return text

        except Exception as e:
            logger.error(f"Error during Gemini CLI generation: {e}", exc_info=True)
            return f"Error during Gemini CLI generation: {e}"

    def _generate_via_sdk(self, prompt: str, context: str = "", output_format: str = "text") -> str:
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
            
            # If no API key, we assume the environment is already configured (e.g. gcloud auth)
            # or the user has a local setup that google-generativeai can detect.
            
            model = genai.GenerativeModel('gemini-3-flash-preview')
            
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{context}\n\nUser Request: {prompt}"
            
            if output_format == "json":
                full_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. Do not include markdown code blocks or any other text."
            elif output_format == "markdown":
                full_prompt += "\n\nIMPORTANT: Use Markdown formatting."
            
            response = model.generate_content(full_prompt)
            text = response.text
            
            # Simple cleanup if AI includes markdown code blocks
            if output_format == "json" and text.startswith("```json"):
                text = text.replace("```json", "", 1).replace("```", "", 1).strip()
            elif output_format == "json" and text.startswith("```"):
                text = text.replace("```", "", 1).replace("```", "", 1).strip()
                
            return text
        except Exception as e:
            logger.error(f"Error during Gemini generation: {e}", exc_info=True)
            return f"Error during Gemini generation: {e}. (Hint: Check your GEMINI_API_KEY or local authentication)"

@time_it(logger)
def generate_ai_response(prompt: str, context: str = "", output_format: str = "text", plugin_manager: PluginManager = None, provider_name: str = None) -> str:
    """Generates a response from the AI given a prompt and optional context."""
    if plugin_manager:
        plugin_manager.trigger_hook("pre_ai_generation", prompt=prompt)

    logger.info(f"Generating AI response. Provider: {provider_name}, Format: {output_format}", extra={"prompt_length": len(prompt), "context_length": len(context)})
    
    if not provider_name:
        provider_name = os.environ.get("ARIA_DEFAULT_AI_PROVIDER", "gemini")

    provider = None
    if plugin_manager:
        provider = plugin_manager.get_ai_provider(provider_name)
    
    # Fallback to built-in Gemini if no provider found or no plugin manager
    if not provider and provider_name == "gemini":
        provider = GeminiProvider({"version": VERSION}) # Minimal context

    if not provider:
        error_msg = f"Error: AI provider '{provider_name}' not found."
        logger.error(error_msg)
        return error_msg

    text = provider.generate(prompt, context, output_format)
    
    logger.info("AI response generated successfully.", extra={"response_length": len(text)})
    
    if plugin_manager:
        plugin_manager.trigger_hook("post_ai_generation", prompt=prompt, response=text)

    return text

def summarize_text(text: str, output_format: str = "text", plugin_manager: PluginManager = None, provider_name: str = None) -> str:
    """Summarizes the given text using the Gemini API."""
    prompt = "Summarize the following text:"
    if output_format == "json":
        prompt = "Summarize the following text and return it as valid JSON with keys 'summary', 'key_points' (list), and 'overall_sentiment':"
    return generate_ai_response(prompt, text, output_format=output_format, plugin_manager=plugin_manager, provider_name=provider_name)

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

def site_synthesize(prompt, sm):
    """Aggregates all site data and uses AI to answer a prompt."""
    print("Synthesizing data from all sites...")
    sites = sm.list_sites()
    all_context = []
    
    for site in sites:
        site_dir = sm.get_site_dir(site)
        files = [f for f in os.listdir(site_dir) if f.endswith(".json") and f != "registry.json"]
        
        site_data_summary = []
        for f in files:
            data = sm.load_data(site, f)
            if not data: continue
            
            if site == "calendar":
                # Add all events
                events = data if isinstance(data, list) else data.get("items", [])
                for ev in events:
                    site_data_summary.append(f"Event: {ev.get('summary')}")
            elif "messages" in data:
                # Add last 10 messages from each thread for context
                msgs = data["messages"][-10:]
                site_data_summary.append(f"Thread/Convo {data.get('name') or data.get('display_name') or f}:")
                for m in msgs:
                    site_data_summary.append(f"  [{m.get('timestamp')}] {m.get('user')}: {m.get('text')}")
        
        if site_data_summary:
            all_context.append(f"--- Data from {site} ---")
            all_context.extend(site_data_summary)

    full_context = "\n".join(all_context)
    
    system_prompt = """
    You are Aria, an intelligent personal assistant. 
    You have access to the user's messages (WhatsApp, Discord, Google Messages, Threads) and Calendar.
    Your goal is to help the user achieve real-world objectives.
    When suggested a goal like "coffee with a friend", look for:
    1. Active conversations or friends mentioned.
    2. Free spots in the calendar.
    3. Proactively suggest WHO, WHEN, and WHERE.
    """
    
    if not prompt:
        prompt = "Based on my recent messages and calendar, what's a good proactive goal for me today or tomorrow? (e.g. who should I meet for coffee?)"

    print("Generating AI response...")
    # Combine system instructions and data into the context
    context = f"{system_prompt}\n\nSite Data:\n{full_context}"
    response = generate_ai_response(prompt, context=context)
    print("\n--- Aria Synthesis ---")
    print(response)

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
    
    # Initialize core managers (without navigator yet)
    script_manager = ScriptManager()
    safety_manager = SafetyManager()
    report_manager = ReportManager()

    # Initial context
    context = {
        "script_manager": script_manager,
        "safety_manager": safety_manager,
        "report_manager": report_manager,
        "version": VERSION
    }

    plugin_manager = PluginManager(context=context)
    
    # We must load plugins BEFORE we can use custom navigators or AI providers
    plugin_manager.load_plugins()

    # Register default Gemini provider if not present (allows Navigator to use it)
    if "gemini" not in plugin_manager.list_ai_providers():
        plugin_manager.ai_providers["gemini"] = GeminiProvider({"version": VERSION})
        logger.info("Registered default GeminiProvider as 'gemini'.")

    if len(sys.argv) > 2 and sys.argv[1] == 'page':
        if sys.argv[2] not in ['new', 'list', 'goto', 'interact', 'summarize', 'tag', 'export', '-h', '--help']:
            # Assume sys.argv[2] is an identifier
            # If sys.argv[3] is 'goto', 'interact', 'summarize', 'tag', 'export', swap them
            if len(sys.argv) > 3 and sys.argv[3] in ['goto', 'interact', 'summarize', 'tag', 'export']:
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
    parser.add_argument('--provider', type=str, help='The AI provider to use for generation.')
    parser.add_argument('--navigator', type=str, default='aria', help='The navigator engine to use.')
    parser.add_argument('-v', '--version', action='store_true', help='Show version information.')
    
    subparsers = parser.add_subparsers(dest="command", required=False)

    # Define the 'help' command
    subparsers.add_parser('help', help='Show this help message and exit.')

    # Define the 'open' command
    parser_open = subparsers.add_parser('open', help='Open a browser instance.')
    parser_open.add_argument('url', type=str, nargs='?', help='Optional URL to navigate to.')
    parser_open.add_argument('--headless', action='store_true', help='Run the browser in headless mode.')
    parser_open.add_argument('--browser', type=str, default='firefox', choices=['chrome', 'firefox', 'edge'], help='The browser to use.')
    parser_open.add_argument('--profile', type=str, help='The name or path of the browser profile to use (Firefox only).')
    parser_open.add_argument('--silence-audio', action='store_true', help='Silence audio in Firefox browser (for undetected geckodriver)')
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
    parser_page_goto.add_argument('--search', action='store_true', help='Perform an AI-driven search.')
    parser_page_goto.add_argument('--first-result', action='store_true', help='Automatically click the first result (implied by --search).')
    parser_page_goto.add_argument('--prompt-result', type=str, help='Prompt to interact with the search results page.')
    parser_page_goto.add_argument('--tries', type=int, default=5, help='Maximum number of results pages to search through.')

    parser_page_interact = page_subparsers.add_parser('interact', help='Interact with the page using AI.')
    parser_page_interact.add_argument('identifier', type=str, nargs='?', help='The index (0-based), ID or title of the page.')
    parser_page_interact.add_argument('prompt', type=str, help='Instruction for interaction (e.g. "Click the login button").')

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

    # Define the 'site' command
    parser_site = subparsers.add_parser('site', help='Manage site-specific data and scraping.')
    site_subparsers = parser_site.add_subparsers(dest="site_command")
    
    parser_site_list = site_subparsers.add_parser('list', help='List all sites with local data.')
    
    parser_site_refresh = site_subparsers.add_parser('refresh', help='Refresh data for a specific site.')
    parser_site_refresh.add_argument('site_name', type=str, help='The name of the site (e.g., google-messages) or "all".')
    parser_site_refresh.add_argument('--deep', action='store_true', help='Perform a deep crawl (follows all thread links, etc). Default is False.')
    
    parser_site_synthesize = site_subparsers.add_parser('synthesize', help='Synthesize data across all sites to answer a prompt or suggest goals.')
    parser_site_synthesize.add_argument('prompt', type=str, nargs='?', help='The question or goal to achieve (e.g. "Suggest someone for coffee tomorrow").')

    parser_site_show = site_subparsers.add_parser('show', help='Show local data for a site.')
    parser_site_show.add_argument('site_name', choices=['google-messages', 'whatsapp', 'discord', 'calendar', 'threads', 'youtube-studio'], help='The name of the site.')
    parser_site_show.add_argument('action', nargs='?', help='Action to perform (recent, list, feed, mine, responses, stats, or <id> for show).')
    parser_site_show.add_argument('sub_action', nargs='?', help='Secondary action (e.g., "show" or "people" when an ID is provided).')
    parser_site_show.add_argument('extra_action', type=str, nargs='?', help='Tertiary action (used for Discord channels).')

    # Define the 'diag' command
    subparsers.add_parser('diag', help='Show diagnostic information.')

    # Define the 'settings' command
    parser_settings = subparsers.add_parser('settings', help='Show current configuration.')
    settings_subparsers = parser_settings.add_subparsers(dest="settings_command")
    
    parser_settings_credentials = settings_subparsers.add_parser('credentials', help='Manage stored credentials.')
    cred_subparsers = parser_settings_credentials.add_subparsers(dest="cred_command")
    
    parser_cred_set = cred_subparsers.add_parser('set', help='Set a credential.')
    parser_cred_set.add_argument('key', type=str, help='The name of the credential.')
    parser_cred_set.add_argument('value', type=str, nargs='?', help='The value of the credential. If omitted, you will be prompted.')
    
    cred_subparsers.add_parser('list', help='List all stored credential keys.')
    
    parser_cred_remove = cred_subparsers.add_parser('remove', help='Remove a stored credential.')
    parser_cred_remove.add_argument('key', type=str, help='The name of the credential to remove.')

    settings_subparsers.add_parser('cleanup', help='Clean up stale session files and orphaned driver processes.')

    parser_settings_export = settings_subparsers.add_parser('export-artifacts', help='Package and export execution artifacts (logs, reports).')
    parser_settings_export.add_argument('--path', type=str, help='Output path for the archive (e.g., run-artifacts.zip).')

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

    if args.version:
        print(f"aria CLI version {VERSION}")
        return

    if not args.command or args.command == 'help':
        parser.print_help()
        return

    if args.force:
        os.environ["ARIA_NON_INTERACTIVE"] = "true"

    # Instantiate the selected navigator
    nav_name = args.navigator
    nav_class = plugin_manager.get_navigator(nav_name)
    
    if not nav_class:
        if nav_name == 'aria':
            nav_class = AriaNavigator
        else:
            print(f"Error: Navigator '{nav_name}' not found. Falling back to 'aria'.")
            nav_class = AriaNavigator
            
    navigator = nav_class()
    navigator.plugin_manager = plugin_manager
    
    # Update plugin context with the final navigator
    plugin_manager.context["navigator"] = navigator
    
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
            if navigator.start_session(browser_name=browser_to_open, headless=args.headless, profile=args.profile, silence_audio=args.silence_audio):
                if url_to_navigate:
                    safe_navigate(url_to_navigate, navigator, safety_manager, force=args.force)
        else:
            print(f"Scope '{args.scope}' is not yet implemented.")
    elif args.command == 'close':
        navigator.close_session(args.browser)
    elif args.command == 'page':
        if args.page_command == 'new':
            if args.scope == 'local':
                if not args.prompt:
                    print("Error: Prompt is required for 'local' scope.")
                    return
                
                print(f"Generating local content for: {args.prompt}")
                
                # Check if it looks like a file system query
                is_fs_query = any(word in args.prompt.lower() for word in ['find', 'list', 'search', 'files', 'directory', 'disk', 'size'])
                
                if is_fs_query:
                    # Use AI to generate a safe shell command
                    system_context = f"Operating System: {os.name}, Platform: {sys.platform}"
                    cmd_prompt = f"Convert the following request into a single safe shell command. {system_context}\nRequest: {args.prompt}\n\nReturn ONLY the command, no markdown, no explanation."
                    command = generate_ai_response(cmd_prompt, provider_name=args.provider).strip()
                    
                    # Basic safety check for generated command
                    forbidden = [';', '&&', '||', '|', '>', 'rm ', 'rf ', 'format', 'mkfs', 'dd ']
                    # We allow some pipes if they are simple, but let's be conservative
                    if any(f in command for f in forbidden if f != '|') or '..' in command:
                        print(f"Safety Check Failed: Generated command looks potentially unsafe: {command}")
                        if not args.force and not safety_manager.confirm("Do you want to run it anyway?"):
                            return

                    import subprocess
                    try:
                        print(f"Running command: {command}")
                        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
                        content = f"<h2>Local Command Results</h2><p>Command: <code>{command}</code></p><pre>{result.stdout}\n{result.stderr}</pre>"
                    except Exception as e:
                        content = f"<h2>Error Running Local Command</h2><pre>{str(e)}</pre>"
                else:
                    # Just generate general HTML content
                    gen_prompt = f"Generate a standalone HTML page (body content only) based on this request: {args.prompt}"
                    content = generate_ai_response(gen_prompt, provider_name=args.provider)

                # Create temp file and open it
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode='w', encoding='utf-8') as f:
                    f.write(f"<html><head><title>Aria Local Page</title><style>body{{font-family:sans-serif;padding:20px;}}pre{{background:#f0f0f0;padding:10px;}}</style></head><body>{content}</body></html>")
                    temp_path = f.name
                
                file_url = f"file://{os.path.abspath(temp_path)}"
                if navigator.start_session(browser_name=args.browser, headless=args.headless, silence_audio=getattr(args, 'silence_audio', False)):
                    navigator.new_tab(file_url)
                    print(f"Opened local results page: {file_url}")
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
                    result = generate_ai_response(refined_prompt, context, output_format=args.format, plugin_manager=plugin_manager, provider_name=args.provider)
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
            
            if args.search:
                if not args.prompt:
                    print("Error: --prompt is required when using --search.")
                    return
                
                print(f"Planning search for: '{args.prompt}'...")
                ai_query = (
                    f"The user wants to search for: '{args.prompt}'.\n"
                    "1. Select the most appropriate search engine for this query (e.g., Google for general, YouTube for video, GitHub for code, etc.).\n"
                    "2. Construct the full URL for the search results page.\n"
                    "Return ONLY a JSON object: {\"url\": \"...\", \"engine\": \"...\"}"
                )
                
                response = generate_ai_response(ai_query, plugin_manager=plugin_manager, provider_name=args.provider, output_format="json")
                try:
                    import json
                    data = json.loads(response)
                    target_url = data.get("url")
                    
                    if target_url:
                        print(f"AI selected search engine: {data.get('engine', 'unknown')}")
                        print(f"Navigating to results: {target_url}")
                        if not safe_navigate(target_url, navigator, safety_manager, force=args.force):
                            return

                        # Result Evaluation Loop
                        interaction_prompt = args.prompt_result or "the first relevant result"
                        max_pages = args.tries
                        
                        for page_num in range(1, max_pages + 1):
                            print(f"\n--- Analyzing Results Page {page_num} ---")
                            import time
                            time.sleep(3) # Wait for results to render
                            
                            links = navigator.extract_links()
                            if not links:
                                print("No links found on the page.")
                                break
                                
                            context_str = json.dumps(links, indent=2)
                            eval_query = (
                                f"You are analyzing a page of search results. The user is looking for: '{interaction_prompt}'.\n\n"
                                f"Current Page Links:\n{context_str}\n\n"
                                "Instructions:\n"
                                "1. If a link clearly matches what the user is looking for, return: {\"url\": \"THE_LINK_URL\"}.\n"
                                "2. If NO link matches but there is a 'Next', 'More', or page number link to see more results, return: {\"next_page_url\": \"THE_NEXT_PAGE_URL\"}.\n"
                                "3. If no match is found and no next page is available, return: {\"error\": \"Not found\"}.\n"
                                "Return ONLY valid JSON."
                            )
                            
                            print("Evaluating search results with AI...")
                            eval_response = generate_ai_response(eval_query, plugin_manager=plugin_manager, provider_name=args.provider, output_format="json")
                            
                            try:
                                # Simple cleanup if AI includes markdown code blocks
                                if eval_response.startswith("```"):
                                    eval_response = eval_response.split("\n", 1)[1].rsplit("\n", 1)[0]
                                
                                eval_data = json.loads(eval_response)
                                
                                if "url" in eval_data:
                                    final_url = eval_data["url"]
                                    print(f"AI found matching result: {final_url}")
                                    navigator.navigate(final_url)
                                    return
                                elif "next_page_url" in eval_data:
                                    next_url = eval_data["next_page_url"]
                                    print(f"AI did not find match on this page. Navigating to next page: {next_url}")
                                    navigator.navigate(next_url)
                                    # Continue loop to next page
                                elif "error" in eval_data:
                                    print(f"AI could not find a match: {eval_data['error']}")
                                    break
                                else:
                                    print("AI returned unrecognized response format.")
                                    break
                            except Exception as e:
                                print(f"Error parsing AI evaluation: {e}")
                                break
                        
                        print("Search completed without finding a definitive match.")
                        return
                except Exception as e:
                    print(f"Search planning failed: {e}. Falling back to default search.")
                    # Fallback to duckduckgo handled below via args.prompt logic if we don't return

            if args.scope == 'bookmarks':
                if not args.prompt:
                    print("Error: Prompt is required for 'bookmarks' scope.")
                    return
                
                aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
                bookmarks_file = os.path.join(aria_dir, "bookmarks.json")
                
                if not os.path.exists(bookmarks_file):
                    print(f"Bookmarks scope: No bookmarks found. Create '{bookmarks_file}' to use this feature.")
                    print("Example format: [{\"title\": \"Example\", \"url\": \"https://example.com\"}]")
                    return
                
                try:
                    with open(bookmarks_file, 'r') as f:
                        bookmarks = json.load(f)
                    
                    # Use AI to find the best match
                    bm_context = json.dumps(bookmarks[:50]) # Limit context
                    find_prompt = f"From the following list of bookmarks, find the one that best matches the request: '{args.prompt}'\n\nBookmarks: {bm_context}\n\nReturn ONLY the URL of the best match, or 'NONE' if no good match is found."
                    match_url = generate_ai_response(find_prompt, provider_name=args.provider).strip()
                    
                    if match_url != "NONE" and (match_url.startswith("http") or match_url.startswith("file")):
                        print(f"Found matching bookmark: {match_url}")
                        safe_navigate(match_url, navigator, safety_manager, force=args.force)
                    else:
                        print(f"No matching bookmark found for: {args.prompt}")
                except Exception as e:
                    print(f"Error reading bookmarks: {e}")
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

        elif args.page_command == 'interact':
            if args.identifier:
                identifier = args.identifier
                try:
                    identifier = int(identifier)
                except ValueError:
                    pass
                if not navigator.goto_tab(identifier):
                    print(f"Error: Could not switch to page '{identifier}'.")
                    return
            
            navigator.navigate_with_prompt(args.prompt)

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
                    result = generate_ai_response(refined_prompt, context, output_format=args.format, plugin_manager=plugin_manager, provider_name=args.provider)
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
                summary = summarize_text(f"{prompt}\n\n{content}", output_format=args.format, plugin_manager=plugin_manager, provider_name=args.provider)
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
            result = generate_ai_response(refined_prompt, context, plugin_manager=plugin_manager, provider_name=args.provider)
            title = args.title or "General Report"
            metrics = get_performance_metrics()
            if args.format == 'html':
                path = report_manager.generate_html_report(title, result, sources=navigator.list_active_browsers(), metrics=metrics)
            else:
                path = report_manager.generate_markdown_report(title, result, sources=navigator.list_active_browsers(), metrics=metrics)
            print(f"Report generated: {path}")
        elif args.report_command == 'list':
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
    elif args.command == 'site':
        sm = SiteManager()
        if args.site_command == 'list':
            sites = sm.list_sites()
            if sites:
                print("Sites with local data:")
                for s in sites:
                    print(f"- {s}")
            else:
                print("No sites with local data found.")
        elif args.site_command == 'refresh':
            site_name = args.site_name
            # Define target URLs for sites
            site_urls = {
                "google-messages": "https://messages.google.com/web/conversations",
                "whatsapp": "https://web.whatsapp.com/",
                "discord": "https://discord.com/app",
                "calendar": "https://calendar.google.com/calendar/u/0/r",
                "threads": "https://www.threads.net/",
                "youtube-studio": "https://studio.youtube.com/"
            }
            
            scrapers_map = {
                "google-messages": GoogleMessagesScraper,
                "whatsapp": WhatsAppScraper,
                "discord": DiscordScraper,
                "threads": ThreadsScraper,
                "calendar": CalendarScraper,
                "youtube-studio": YouTubeStudioScraper
            }

            sites_to_refresh = []
            if site_name == "all":
                sites_to_refresh = list(site_urls.keys())
            else:
                if site_name not in site_urls:
                    print(f"Refresh logic for site '{site_name}' is not yet implemented.")
                    return
                sites_to_refresh = [site_name]

            browser_name = getattr(args, 'browser', 'firefox')
            
            for sn in sites_to_refresh:
                print(f"\n--- Refreshing data for {sn} ---")
                target_url = site_urls[sn]
                
                # Try to find existing tab first
                found = False
                if navigator.connect_to_session(browser_name=browser_name):
                    if navigator.find_tab_by_url(target_url):
                        print(f"Found existing tab for {sn}. Reusing it.")
                        found = True
                
                if not found:
                    headless = getattr(args, 'headless', False)
                    profile = getattr(args, 'profile', None)
                    if not navigator.start_session(browser_name=browser_name, headless=headless, profile=profile):
                        print(f"Failed to start session for {sn}.")
                        continue
                    # Check again in the new session just in case
                    if not navigator.find_tab_by_url(target_url):
                        print(f"Navigating to {target_url}...")
                        navigator.navigate(target_url)

                # Dispatch to scraper
                if sn in scrapers_map:
                    scraper = scrapers_map[sn](navigator, sm)
                    # Pass the deep flag to the refresh method
                    if scraper.refresh(deep=getattr(args, 'deep', False)):
                        print(f"Successfully refreshed data for {sn}.")
                    else:
                        print(f"Failed to refresh data for {sn}.")
                else:
                    print(f"Scraper for '{sn}' is not yet fully implemented.")
        elif args.site_command == 'synthesize':
            site_synthesize(args.prompt, sm)
        elif args.site_command == 'show':
            site_name = args.site_name
            sm = SiteManager()
            reg = sm.get_registry(site_name)
            mappings = reg.get("mappings", {})
            
            # Handle numerical ID if provided as 'action'
            item_name = None
            if args.action and args.action.isdigit():
                item_name = mappings.get(args.action)
                if not item_name:
                    print(f"Error: No conversation with ID {args.action} found in registry.")
                    return
            
            # 1. Action: list
            if args.action == 'list':
                if site_name == "calendar":
                    events = sm.load_data(site_name, "events.json")
                    if events:
                        print(f"Calendar events for {site_name}:")
                        for i, ev in enumerate(events):
                            print(f"{i+1}: {ev['summary']}")
                    else:
                        print(f"No events found for {site_name}. Run 'site refresh calendar' first.")
                    return
                elif site_name == "youtube-studio":
                    videos = sm.load_data(site_name, "videos.json")
                    if videos:
                        print(f"Videos for {site_name}:")
                        for i, v in enumerate(videos):
                            print(f"{i+1}: {v['title']} ({v['views']} views)")
                    else:
                        print(f"No videos found for {site_name}. Run 'site refresh youtube-studio' first.")
                    return

                if mappings:
                    print(f"Items for {site_name} (Persistent IDs):")
                    for cid in sorted(mappings.keys(), key=int):
                        print(f" {cid:3}: {mappings[cid]}")
                else:
                    print(f"No items indexed for {site_name}. Run 'site refresh {site_name}' first.")
            
            # 2. Action: <id> list (Specific to Discord for listing channels)
            elif site_name == "discord" and item_name and args.sub_action == 'list':
                # Find all chat_ServerName_*.json files
                safe_server = "".join([c if c.isalnum() else "_" for c in item_name])
                site_dir = sm.get_site_dir(site_name)
                files = [f for f in os.listdir(site_dir) if f.startswith(f"chat_{safe_server}_") and f.endswith(".json")]
                
                if files:
                    print(f"Channels in {item_name}:")
                    for f in files:
                        # Extract channel name from filename: chat_Server_Channel.json
                        chan_name = f.replace(f"chat_{safe_server}_", "").replace(".json", "")
                        print(f"- {chan_name}")
                else:
                    print(f"No channels found for server {item_name}.")

            # 3. Action: <id> show
            elif item_name and (args.sub_action == 'show' or args.extra_action == 'show'):
                if site_name in ["google-messages", "whatsapp", "threads"]:
                    if site_name == "discord":
                        # Handled below
                        pass
                    else:
                        safe_name = "".join([c if c.isalnum() else "_" for c in item_name])
                        # Try convo_ prefix first, then thread_
                        data = sm.load_data(site_name, f"convo_{safe_name}.json") or \
                               sm.load_data(site_name, f"thread_{safe_name}.json")
                        
                        # Special case for Threads IDs which aren't safe_names but exact IDs in the registry
                        if not data and site_name == "threads":
                            site_dir = sm.get_site_dir(site_name)
                            all_files = [f for f in os.listdir(site_dir) if f.startswith("thread_") and f.endswith(".json")]
                            for f in all_files:
                                d = sm.load_data(site_name, f)
                                if d and d.get("display_name") == item_name:
                                    data = d
                                    break

                        if data and "messages" in data:
                            print(f"Messages for {item_name}:")
                            for msg in data["messages"]:
                                prefix = ">>" if msg.get("type") == "sent" else "<<"
                                ts = f"[{msg['timestamp']}] " if msg.get('timestamp') and msg['timestamp'] != "Unknown" else ""
                                likes = f" ({msg['likes']} likes)" if 'likes' in msg and msg['likes'] > 0 else ""
                                print(f"{ts}{msg.get('user', 'User')}: {prefix} {msg.get('text', '')}{likes}")
                        else:
                            print(f"No message data found for {item_name}.")
                        return

            # Detailed Browsing for Threads
            elif site_name == "threads" and args.action in ["mine", "responses", "stats", "feed"]:
                site_dir = sm.get_site_dir(site_name)
                metadata = sm.load_data(site_name, "metadata.json") or {}
                profile_url = metadata.get("profile_url", "")
                own_user = profile_url.split('/@')[-1] if profile_url else "oulupoko"
                
                all_threads = [f for f in os.listdir(site_dir) if f.startswith("thread_") and f.endswith(".json")]
                all_messages = []
                for f in all_threads:
                    data = sm.load_data(site_name, f)
                    if data and "messages" in data:
                        # Mark if thread started by someone else (for 'responses')
                        first_user = data["messages"][0].get("user", "")
                        for msg in data["messages"]:
                            msg["_thread_url"] = data.get("url", "")
                            msg["_thread_starter"] = first_user
                            all_messages.append(msg)

                if args.action == "mine":
                    print(f"Own messages for {own_user}:")
                    mine = [m for m in all_messages if m.get("user") == own_user]
                    for m in mine:
                        ts = f"[{m['timestamp']}] " if m['timestamp'] != "Unknown" else ""
                        print(f"{ts}{m['text'][:150]}...")

                elif args.action == "responses":
                    print(f"Responses by {own_user} to other threads:")
                    # Responses are our messages in threads started by others
                    responses = [m for m in all_messages if m.get("user") == own_user and m.get("_thread_starter") != own_user]
                    for m in responses:
                        ts = f"[{m['timestamp']}] " if m['timestamp'] != "Unknown" else ""
                        print(f"{ts}To {m['_thread_starter']}: {m['text'][:150]}...")

                elif args.action == "feed":
                    print(f"Cached General Feed for {site_name}:")
                    feed_data = sm.load_data(site_name, "feed.json")
                    if not feed_data:
                        print("No feed data cached. Run refresh first.")
                    else:
                        for i, post in enumerate(feed_data):
                            ts = f"[{post['timestamp']}] " if post.get('timestamp') and post['timestamp'] != "Unknown" else ""
                            likes = f" ({post['likes']} likes)" if 'likes' in post and post['likes'] > 0 else ""
                            print(f"{i+1}: {ts}{post['user']}: {post['text'][:150]}{likes}...")

                elif args.action == "stats":
                    print(f"Engagement Statistics for {site_name}:")
                    liked = [m for m in all_messages if m.get("likes", 0) > 0]
                    if not liked:
                        print("No liked messages found in cache.")
                    else:
                        sorted_liked = sorted(liked, key=lambda x: x.get("likes", 0), reverse=True)
                        print("\nTop 5 Most Liked Messages:")
                        for m in sorted_liked[:5]:
                            print(f"- ({m['likes']} likes) {m['user']}: {m['text'][:100]}...")
                        
                        print("\nLeast Liked (among those with likes):")
                        for m in sorted_liked[-3:]:
                            print(f"- ({m['likes']} likes) {m['user']}: {m['text'][:100]}...")
                return

            # 3. Action: <id> people
            elif item_name and args.sub_action == 'people':
                # For now, we often only have the conversation name as the 'person' 
                # unless it's a group or we extract phone numbers.
                # Heuristic: if name contains numbers, it might be a phone number.
                print(f"Participants in {item_name}:")
                print(f"- {item_name}")
                # TODO: Implement deeper extraction of group participants if available in JSON

            # 4. Action: recent (Default)
            elif (args.action in ['recent', 'feed', 'mine', 'responses', 'stats'] and not args.sub_action) or (not args.action and not item_name):
                if site_name in ["google-messages", "whatsapp", "threads"]:
                    site_dir = sm.get_site_dir(site_name)
                    
                    # For messaging sites, look for convo_*.json
                    files = [f for f in os.listdir(site_dir) if f.startswith("convo_") and f.endswith(".json")]
                    # For feed-based sites, look for feed.json
                    feed_file = os.path.join(site_dir, "feed.json")
                    
                    recent_items = []
                    
                    # Process conversations
                    for f in files:
                        data = sm.load_data(site_name, f)
                        if data and "messages" in data and data["messages"]:
                            last_msg = data["messages"][-1]
                            recent_items.append({
                                "source": data.get("name", "Unknown"),
                                "text": last_msg.get("text", "[Media]"),
                                "timestamp": last_msg.get("timestamp", ""),
                                "type": last_msg.get("type", "")
                            })
                    
                    # Process feed
                    if os.path.exists(feed_file):
                        feed_data = sm.load_data(site_name, "feed.json")
                        if feed_data:
                            # Add last 5 posts
                            for post in feed_data[:5]:
                                recent_items.append({
                                    "source": post.get("user", "Post"),
                                    "text": post.get("text", ""),
                                    "timestamp": post.get("timestamp", ""),
                                    "type": "received"
                                })

                    if recent_items:
                        print(f"Recent items from {site_name}:")
                        for item in sorted(recent_items, key=lambda x: str(x["timestamp"]), reverse=True)[:15]:
                            prefix = ">>" if item.get("type") == "sent" else "<<"
                            ts_display = f"[{item['timestamp']}] " if item['timestamp'] and item['timestamp'] != "Unknown" else ""
                            print(f"{ts_display}{item['source']}: {prefix} {item['text']}")
                    else:
                        print(f"No recent items found for {site_name}. Run 'site refresh {site_name}' first.")
                else:
                    # Generic fallback
                    data = sm.get_recent_items(site_name, "conversations.json") or sm.get_recent_items(site_name, "events.json")
                    if data:
                        print(f"Recent items for {site_name}:")
                        import json
                        print(json.dumps(data, indent=2))
                    else:
                        print(f"No recent data found for {site_name}. Run 'site refresh {site_name}' first.")
            else:
                parser_site_show.print_help()
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
        if args.settings_command == 'credentials':
            cm = CredentialManager()
            if args.cred_command == 'set':
                key = args.key
                value = args.value
                if not value:
                    import getpass
                    value = getpass.getpass(f"Enter value for '{key}': ")
                cm.set_credential(key, value)
                print(f"Credential '{key}' set successfully.")
            elif args.cred_command == 'list':
                keys = cm.list_keys()
                if keys:
                    print("Stored Credentials (keys only):")
                    for k in keys:
                        print(f"- {k}")
                else:
                    print("No credentials stored.")
            elif args.cred_command == 'remove':
                if cm.remove_credential(args.key):
                    print(f"Credential '{args.key}' removed successfully.")
                else:
                    print(f"Error: Credential '{args.key}' not found.")
            else:
                parser_settings_credentials.print_help()
        elif args.settings_command == 'cleanup':
            count = navigator.cleanup_orphaned_sessions()
            print(f"Cleanup complete. Removed {count} stale session(s).")
        elif args.settings_command == 'export-artifacts':
            import shutil
            import tempfile
            from datetime import datetime
            
            aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_path = f"aria_artifacts_{timestamp}"
            output_path = args.path or default_path
            
            # Use a temp directory to collect files safely
            with tempfile.TemporaryDirectory() as tmpdir:
                # Copy logs
                log_file = os.path.join(aria_dir, "aria.log")
                if os.path.exists(log_file):
                    shutil.copy2(log_file, tmpdir)
                
                # Copy reports
                reports_dir = os.path.join(aria_dir, "reports")
                if os.path.exists(reports_dir):
                    shutil.copytree(reports_dir, os.path.join(tmpdir, "reports"), dirs_exist_ok=True)
                
                # Copy metadata (not credentials)
                scripts_dir = os.path.join(aria_dir, "scripts")
                if os.path.exists(scripts_dir):
                    # Only copy metadata.json, not the whole dir if there are local scripts
                    meta = os.path.join(scripts_dir, "metadata.json")
                    if os.path.exists(meta):
                        os.makedirs(os.path.join(tmpdir, "scripts"), exist_ok=True)
                        shutil.copy2(meta, os.path.join(tmpdir, "scripts"))
                
                # Make archive
                # shutil.make_archive appends extension if not present
                base_name = output_path
                if base_name.endswith('.zip'):
                    base_name = base_name[:-4]
                
                final_path = shutil.make_archive(base_name, 'zip', tmpdir)
                print(f"Artifacts exported to: {final_path}")
        else:
            aria_dir = os.path.join(os.path.expanduser("~"), ".aria")
            print(f"Aria Configuration:")
            print(f"  Aria Home:         {aria_dir}")
            print(f"  Scripts Directory: {os.path.join(aria_dir, 'scripts')}")
            print(f"  Plugins Directory: {os.path.join(aria_dir, 'plugins')}")
            print(f"  Default Provider:  {os.environ.get('ARIA_DEFAULT_AI_PROVIDER', 'gemini')}")
            print(f"  Log Level:         {logging.getLevelName(logger.getEffectiveLevel())}")
            print(f"  Current Browser:   {navigator._get_current_browser()}")
            print(f"  Active Browsers:   {', '.join(navigator.list_active_browsers())}")
            print(f"  Non-Interactive:   {os.environ.get('ARIA_NON_INTERACTIVE', 'false')}")

    elif args.command == 'man':
        print("ARIA(1)                          Aria User Manual                         ARIA(1)")
        print("\nNAME")
        print("    aria - AI-driven web automation assistant")
        print("\nSYNOPSIS")
        print("    aria [GLOBAL_OPTIONS] COMMAND [ARGS...]")
        print("\nDESCRIPTION")
        print("    Aria is a powerful CLI tool that leverages AI to automate web browsing tasks.")
        print("    It manages browser sessions, tabs (pages), and reusable automation scripts.")
        print("\nGLOBAL OPTIONS")
        print("    --force          Bypass safety warnings and run in non-interactive mode.")
        print("    --slow-mo SEC    Add a delay (in seconds) between browser actions.")
        print("    --navigator NAV  Select navigator engine (default: 'aria').")
        print("    --provider PROV  Select AI provider (default: 'gemini').")
        print("    --log-level LVL  Set logging verbosity (DEBUG, INFO, WARNING, ERROR).")
        print("\nCOMMANDS")
        print("    open [URL] [--browser B] [--headless]")
        print("        Open a browser instance. B can be 'chrome', 'firefox', or 'edge'.")
        print("\n    close [BROWSER]")
        print("        Close browser instances. If BROWSER is omitted, closes all.")
        print("\n    page list")
        print("        List all open tabs with their indices and persistent IDs.")
        print("\n    page new [--url URL] [--prompt PROMPT]")
        print("        Open a new tab. Can navigate directly or generate content via prompt.")
        print("\n    page <id> goto [--url URL] [--prompt PROMPT] [--search] [--first-result] [--prompt-result P]")
        print("        Navigate an existing tab. Use --search for AI-driven navigation.")
        print("        --first-result clicks the first search result automatically.")
        print("        --prompt-result P uses P to interact with the landing page.")
        print("\n    page <id> interact PROMPT")
        print("        Interact with the page using natural language (e.g., 'Click login').")
        print("\n    page <id> summarize [PROMPT]")
        print("        Summarize the content of a tab using AI.")
        print("\n    site list")
        print("        List all sites that have locally stored data.")
        print("\n    site refresh <site_name>")
        print("        Navigate to a site and sync data to local storage (e.g., google-messages).")
        print("\n    site show <site_name> [recent|all]")
        print("        Display locally stored data for a site.")
        print("\n    script run <id> [--param name=value]")
        print("        Execute a saved script. Supports parameter injection.")
        print("\n    settings export-artifacts [--path PATH]")
        print("        Package logs and reports into a ZIP archive for CI/CD collection.")
        print("\n    security")
        print("        Display security best practices for web automation.")
        print("\nFILES")
        print(f"    ~/.aria/         Home directory for configuration, scripts, and logs.")
        print(f"    ~/.aria/aria.log Application logs.")
        print("\nSEE ALSO")
        print("    For full documentation and recipes, see the 'docs/' directory in the source.")

    elif args.command == 'tutorial':
        print("=== WELCOME TO THE ARIA TUTORIAL ===")
        print("\nAria helps you automate the web using natural language.")
        print("\nSTEP 1: Open a browser")
        print("    Run: aria open chrome")
        print("    (Or 'firefox' if you prefer)")
        print("\nSTEP 2: Navigate to a website")
        print("    Run: aria page new --url https://news.ycombinator.com")
        print("\nSTEP 3: See your active tabs")
        print("    Run: aria page list")
        print("    Note the index (0) and the unique ID in parentheses.")
        print("\nSTEP 4: Use AI to understand the page")
        print("    Run: aria page 0 summarize \"What are the top 3 stories?\"")
        print("\nSTEP 5: Create a reusable script")
        print("    Run: aria script new --prompt \"Search for {{query}} on Google\" --name search")
        print("\nSTEP 6: Run your script")
        print("    Run: aria script run search --param query=\"Aria automation\"")
        print("\nSTEP 7: Export your work")
        print("    Run: aria settings export-artifacts")
        print("\nPRO TIP: Use '--force' in CI/CD environments to bypass all prompts.")
        print("\nType 'aria man' for the full manual or 'aria help' for quick syntax.")

    elif args.command == 'version':
        print(f"aria CLI version {VERSION}")
    elif args.command == 'security':
        print(safety_manager.get_security_best_practices())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()