import argparse
import logging
import json
from duplicate_processor import DuplicateProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OptimizedDuplicateFinder:
    def __init__(self, directory, destination):
        # Load configuration from a separate method
        self.config = self.load_config()
        
        self.directory = directory
        self.destination = destination
        self.duplicate_processor = DuplicateProcessor(directory, self.config["database_name"])

    @staticmethod
    def load_config():
        """Load configuration from config.json."""
        try:
            with open('config.json', 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            return {}

    def run(self):
        self.duplicate_processor.process_duplicates()
        logging.info("OptimizedDuplicateFinder script has completed its task.")

def main():
    parser = argparse.ArgumentParser(description="Find and manage duplicate files.")
    parser.add_argument("directory", help="Path to the directory to search.")
    parser.add_argument("destination", help="Path to the destination folder.")
    args = parser.parse_args()
    
    finder = OptimizedDuplicateFinder(args.directory, args.destination)
    finder.run()

if __name__ == "__main__":
    main()
