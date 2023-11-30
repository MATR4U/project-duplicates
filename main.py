import argparse
import logging
from processor import Processor
from utilities import Utilities

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class App:

    def __init__(self, dataSourceDir, dataDestinationDir):
        self.processor = Processor(dataSourceDir, dataDestinationDir)
    
    def run(self):
        logging.info("Starting process store in database...")
        self.processor.record_files()

        logging.info("Starting process find and mark duplicates...")
        self.processor.process_duplicates()
        
        logging.info("Starting process duplicate summary...")
        self.processor.print_duplicates_summary()
        
        # Wait for user confirmation to move duplicates
        user_input = input("Do you want to move the duplicates to the target directory? (yes/no): ")
        if user_input.lower() == "yes":
            self.processor.move_duplicates()
        
        logging.info("Duplicate processing completed.")

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
    app.run()

if __name__ == "__main__":
    main()
