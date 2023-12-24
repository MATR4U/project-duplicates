import os
import shutil
from datetime import datetime
import logging
import json
import random
import requests
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Utilities:
    """Class provides static utilities functions"""
    
    @staticmethod
    def extract_year_from_timestamp(timestamp):
        return datetime.fromisoformat(timestamp).year

    @staticmethod
    def send_notification(message, api_url="https://api.example.com/notifications", api_token="YOUR_API_TOKEN"):
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        data = {
            "message": message
        }
        try:
            response = requests.post(api_url, headers=headers, json=data)
            if response.status_code != 200:
                logging.error("Failed to send notification. API responded with: {response.text}")
            else:
                logging.info("Notification sent successfully.")
        except Exception as e:
            logging.error("Error sending notification: %s", e)

    @staticmethod
    def collect_feedback():
        feedback = input("Please provide your feedback or report any issues: ")
        if feedback:
            try:
                with open("feedback.txt", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.datetime.now()}: {feedback}\n")
                logging.info("Thank you for your feedback!")
            except Exception as e:
                logging.error("Error saving feedback: %s", str(e))

    @staticmethod
    def delete_folders_with_pattern(start_path, patterns):
        """
        Delete folders matching specific patterns.

        Args:
            start_path (str): The path to start searching for folders.
            patterns (list of str): Patterns to match folder names.
        """
        for root, dirs, _ in os.walk(start_path, topdown=False):
            for dir_name in dirs:
                if any(pattern in dir_name for pattern in patterns):
                    folder_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(folder_path)
                        logging.info("Deleted folder: %s", folder_path)
                    except Exception as e:
                        logging.error("Failed to delete folder %s: %s", folder_path, e)

    @staticmethod
    def generate_unique_name(base_path, dir_name):
        """Generate a unique directory name by appending a timestamp and a random number."""
        max_attempts = 5
        for _ in range(max_attempts):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_number = random.randint(100, 999)  # Random number between 100 and 999
            new_dir_name = f"{dir_name}_{timestamp}_{random_number}"
            target_path = os.path.join(base_path, new_dir_name)
            if not os.path.exists(target_path):
                return target_path
        raise Exception("Failed to generate a unique name for %s after %s", dir_name, max_attempts)
    
    @staticmethod
    def process_items_with_pattern(start_path, patterns, target_directory, delete_instead=False):
        """
        Move or delete files and folders matching specific patterns.

        Args:
            start_path (str): The path to start searching.
            patterns (list of str): Patterns to match names.
            target_directory (str): The directory to move items to.
            delete_instead (bool): If True, delete the items instead of moving.
        """
        if not os.path.exists(target_directory) and not delete_instead:
            os.makedirs(target_directory)
            logging.info("Created target directory: %s", target_directory)

        items_to_process = []
        for root, dirs, files in os.walk(start_path, topdown=False):
            for name in dirs + files:
                if any(pattern in name for pattern in patterns):
                    items_to_process.append(os.path.join(root, name))

        with tqdm(total=len(items_to_process), desc="Processing items", unit="item") as progress_bar:
            for item_path in items_to_process:
                name = os.path.basename(item_path)

                if delete_instead:
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                        logging.info("Deleted item: %s", item_path)
                    except Exception as e:
                        logging.error("Failed to delete item %s: %s", item_path, e)

                else:
                    target_path = os.path.join(target_directory, name)
                    if os.path.exists(target_path):
                        try:
                            target_path = Utilities.generate_unique_name(target_directory, name)
                        except Exception as e:
                            logging.error(e)
                            continue

                    try:
                        shutil.move(item_path, target_path)
                        logging.info("Moved item: %s to %s", item_path, target_path)
                    except Exception as e:
                        logging.error("Failed to move item %s to %s: %s", item_path, target_path, e)

                progress_bar.update(1)


