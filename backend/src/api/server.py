import logging
import uvicorn
from fastapi import FastAPI
from src.api.routers.files import router as item_router

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class API:
    """
    Singleton instance
    """
    _instance = None

    def __init__(self):
        """
        Initialize FastAPI instance
        """
        self.instance = FastAPI()

    def run(self):
        """
        Include router and run the FastAPI instance
        """
        try:
            self.instance.include_router(item_router)
            uvicorn.run(self.instance, port=8000)
        except Exception as e:
            """
            Log any exceptions that occur while running the server
            """
            logging.error(f"An error occurred while running the server: {e}")

    @staticmethod
    def get_instance():
        """
        Return the singleton instance
        """
        return API.instance

    @classmethod
    def startup_event(cls):
        """
        Initialize your database or perform any other startup tasks here
        """
        try:
            print("startup fastapi")
            cls.instance.include_router(item_router)
            return cls.instance
        except Exception as e:
            """
            Log any exceptions that occur during startup
            """
            logging.error(f"An error occurred during startup: {e}")