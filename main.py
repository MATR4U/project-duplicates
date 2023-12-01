import argparse
import logging
from processor import Processor
from utilities import Utilities

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class App:

    def __init__(self, dataSourceDir, dataDestinationDir):
        self.processor = Processor(dataSourceDir, dataDestinationDir)
    
    def run(self):

        #TODO Cleanup process should stage the change into a new delete schema, movement of the files should be acknowledged.
        # csv file is exported including the to be deleted data
        #patterns = ['.@__thumb', '.thumbnails', '@eaDir', '.picasa.ini']
        #Utilities.process_items_with_pattern(dataSourceDir, patterns, dataDestinationDir, True)
        #self.processor.export_pattern_summary()

        #TODO if data is already in the database, first should be checked which of the data is still available
        # if data is not available mark is_deleted
        # if data is_deleted marked it should be removed from the duplication schema


        #the filesystem should be checked for new availablae data that is not yet in the database
        logging.info("Starting process store in database...")
        self.processor.add_files()
        #self.processor.export_files_summary()

        # the whole available database should be checked for any duplicates
        # duplicates should be added
        logging.info("Starting process find and mark duplicates...")
        self.processor.add_duplicates()
        #self.processor.export_duplicates_summary()
                
        # Wait for user confirmation to move duplicates
        # user_input = input("Do you want to move the duplicates to the target directory? (yes/no): ")
        #if user_input.lower() == "yes":
        #self.processor.move_duplicates()
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
