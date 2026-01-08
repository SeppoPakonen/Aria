import argparse
from navigator import AriaNavigator

def main():
    parser = argparse.ArgumentParser(description="Aria CLI - Your web automation assistant.")
    subparsers = parser.add_subparsers(dest="command")

    # Define the 'open' command
    parser_open = subparsers.add_parser('open', help='Open a URL in a new browser window.')
    parser_open.add_argument('url', type=str, help='The URL to navigate to.')
    parser_open.add_argument('--headless', action='store_true', help='Run the browser in headless mode.')

    args = parser.parse_args()

    if args.command == 'open':
        navigator = AriaNavigator(headless=args.headless)
        try:
            navigator.navigate(args.url)
            # Keep the browser open for a while for the user to see.
            # In a real scenario, we would not close it immediately
            # or would have a separate 'close' command.
            print(f"Successfully navigated to {args.url}. Browser will close in 30 seconds.")
            import time
            time.sleep(30)
        finally:
            navigator.close()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
