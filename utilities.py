import datetime
import requests
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Utilities:
        
    @staticmethod
    def load_config():
        """Load configuration from config.json."""
        try:
            with open('config.json', 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            return {}
    
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
                logging.error(f"Failed to send notification. API responded with: {response.text}")
            else:
                logging.info("Notification sent successfully.")
        except Exception as e:
            logging.error(f"Error sending notification: {str(e)}")

    @staticmethod
    def collect_feedback():
        feedback = input("Please provide your feedback or report any issues: ")
        if feedback:
            try:
                with open("feedback.txt", "a") as f:
                    f.write(f"{datetime.datetime.now()}: {feedback}\n")
                logging.info("Thank you for your feedback!")
            except Exception as e:
                logging.error(f"Error saving feedback: {str(e)}")
