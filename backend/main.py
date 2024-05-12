import argparse
import logging
from src.App import App


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Help for Usage.")
    parser.add_argument("-s", "--source", type=str, help="Path to the source to search.")
    parser.add_argument("-d", "--destination", type=str, help="Path to the destination folder.")
    parser.add_argument("-b", '--db-url', type=str, help='Database URL (e.g., "postgresql://myuser:mypassword@localhost/mydb")')
    parser.add_argument("-c", "--config", type=str, help="Path to the configuration file.", default="config.json")

    args = parser.parse_args()

    app = App(args)  # convert args from namespace into dictionary
    # TODO app.run()
    app.run_api_server()


if __name__ == "__main__":
    main()