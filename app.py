import logging
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER
from processor import Processor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class App:

    def __init__(self, dataSourceDir, dataDestinationDir):
        self.processor = Processor(dataSourceDir, dataDestinationDir)

    def on_button_click(self, widget):
        print("Hello World!")

    def runUi(self):
        return toga.App('First Toga App', 'org.beeware.helloworld', startup = self.runUiBuild())

    def runUiBuild(self):
        main_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))

        button = toga.Button('Click me', on_press=self.on_button_click, style=Pack(padding=20))
        main_box.add(button)

    def runCli(self):
   
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
