import argparse
import logging
import json
from processor import Processor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class App:

    def __init__(self, dataSourceDir, dataDestinationDir):
        self.processor = Processor(dataSourceDir, dataDestinationDir)
    
    def run(self):
        logging.info("Starting process store in database...")
        #self.processor.get_all_files_batch_optimized()

        logging.info("Starting process find and mark duplicates...")
        self.processor.process_duplicates()
        
        #logging.info("Fetching duplicates summary...")
        # Accessing db_operations via duplicate_processor
        #duplicates = self.processor.db_operations.fetch_duplicates()
        
        # Displaying the duplicates summary
        #for hash_, paths in duplicates.items():
        #    print(f"Hash: {hash_}, Paths: {paths}")
        
        # Wait for user confirmation to move duplicates
        #user_input = input("Do you want to move the duplicates to the target directory? (yes/no): ")
        #if user_input.lower() == "yes":
        #    self.processor.move_confirmed_duplicates(self.destination)
        
        #logging.info("Duplicate processing completed.")

def main():
    parser = argparse.ArgumentParser(description="Find and manage duplicate files.")
    parser.add_argument("directory", help="Path to the directory to search.")
    parser.add_argument("destination", help="Path to the destination folder.")
    args = parser.parse_args()
    
    with open('config.json', 'r') as file:
        config = json.load(file)
    
    finder = App(args.directory, args.destination)
    finder.run()

if __name__ == "__main__":
    main()
