import argparse
from navigator import AriaNavigator

def main():
    parser = argparse.ArgumentParser(description="Aria CLI - Your web automation assistant.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Define the 'open' command
    parser_open = subparsers.add_parser('open', help='Open a URL in a new browser window.')
    parser_open.add_argument('url', type=str, help='The URL to navigate to.')
    parser_open.add_argument('--headless', action='store_true', help='Run the browser in headless mode.')

    # Define the 'close' command
    subparsers.add_parser('close', help='Close the browser window.')

    args = parser.parse_args()

    navigator = AriaNavigator()

    if args.command == 'open':
        if navigator.start_session(headless=args.headless):
            navigator.navigate(args.url)
    elif args.command == 'close':
        navigator.close_session()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
