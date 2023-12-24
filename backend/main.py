import argparse
import logging
from src.app import App

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Help for Usage.")
    parser.add_argument("-dir", "--source", type=str, help="Path to the source to search.")
    parser.add_argument("-dest", "--destination", type=str, help="Path to the destination folder.")
    parser.add_argument("-db", '--db-url', type=str, help='Database URL (e.g., "postgresql://myuser:mypassword@matr-database-postgres/mydb")')
    parser.add_argument("-cfg", "--config", type=str, help="Path to the configuration file.", default="config.json")

    args = parser.parse_args()
    app = App(args)

    #app.runCli()
    #app.runApi()
    #app.runDb()

if __name__ == "__main__":
    main()
