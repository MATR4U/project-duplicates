import argparse
import logging
from utilities import Utilities
from app import App

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Find and manage duplicate files.")
    parser.add_argument("directory", help="Path to the directory to search.", nargs='?', default=None)
    parser.add_argument("destination", help="Path to the destination folder.", nargs='?', default=None)
    parser.add_argument("-c", "--config", help="Path to the configuration file.", default='config.json')
    args = parser.parse_args()

    # Load the configuration file
    config = Utilities.load_config()

    # Override config file values with command line arguments if they are provided
    directory = args.directory if args.directory else config.get('directory')
    destination = args.destination if args.destination else config.get('destination')
    
    app = App(directory, destination)
    app.runCli()

if __name__ == "__main__":
    main()
