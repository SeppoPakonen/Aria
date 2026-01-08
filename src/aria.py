import argparse
from navigator import AriaNavigator

def main():
    parser = argparse.ArgumentParser(description="Aria CLI - Your web automation assistant.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Define the 'open' command
    parser_open = subparsers.add_parser('open', help='Open a URL in a new browser window.')
    parser_open.add_argument('url', type=str, help='The URL to navigate to.')
    parser_open.add_argument('--headless', action='store_true', help='Run the browser in headless mode.')
    parser_open.add_argument('--browser', type=str, default='chrome', choices=['chrome', 'firefox', 'edge'], help='The browser to use.')

    # Define the 'close' command
    subparsers.add_parser('close', help='Close the browser window.')

    # Define the 'page' command
    parser_page = subparsers.add_parser('page', help='Manage browser pages.')
    page_subparsers = parser_page.add_subparsers(dest="page_command", required=True)
    parser_page_new = page_subparsers.add_parser('new', help='Navigate to a new URL.')
    parser_page_new.add_argument('url', type=str, help='The URL to navigate to.')

    args = parser.parse_args()

    navigator = AriaNavigator()

    if args.command == 'open':
        if navigator.start_session(browser_name=args.browser, headless=args.headless):
            navigator.navigate(args.url)
    elif args.command == 'close':
        navigator.close_session()
    elif args.command == 'page':
        if args.page_command == 'new':
            navigator.navigate(args.url)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
