import argparse
from navigator import AriaNavigator

def main():
    parser = argparse.ArgumentParser(description="Aria CLI - Your web automation assistant.")
    subparsers = parser.add_subparsers(dest="command")

    # Define the 'open' command
    parser_open = subparsers.add_parser('open', help='Open a URL in a new browser window.')
    parser_open.add_argument('url', type=str, help='The URL to navigate to.')
    parser_open.add_argument('--headless', action='store_true', help='Run the browser in headless mode.')

    # Define the 'close' command
    parser_close = subparsers.add_parser('close', help='Close the browser window.')

    args = parser.parse_args()

    if args.command == 'open':
        navigator = AriaNavigator(headless=args.headless)
        navigator.navigate(args.url)
        print(f"Successfully navigated to {args.url}. The browser will remain open.")
        # The navigator object is lost after the command finishes.
        # We need a way to persist the driver session.
        # This will be addressed in a future task.
    elif args.command == 'close':
        # This is a placeholder. We need to implement state management
        # to get access to the active navigator instance.
        print("Closing the browser... (This is a placeholder and will be implemented in a future task)")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
