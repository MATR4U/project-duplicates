import argparse
import logging
from src.app import App


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Help for Usage.")
    parser.add_argument("-s", "--source", type=str, help="Path to the source to search.")
    parser.add_argument("-d", "--destination", type=str, help="Path to the destination folder.")
    parser.add_argument("-b", '--db-url', type=str, help='Database URL (e.g., "postgresql://myuser:mypassword@localhost/mydb")')
    parser.add_argument("-c", "--config", type=argparse.FileType('r'), help="Path to the configuration file.", default="config.json")

    args = parser.parse_args()
    app = App(args)

    app.run_db()
    app.run_api()
    

    # Keep the application running until the user presses enter
    print("Press enter to exit the app...")
    input()


if __name__ == "__main__":
    main()