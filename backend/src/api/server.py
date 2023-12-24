
import logging
import uvicorn
from fastapi import FastAPI
from src.api.routers.files import router as item_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
class API:
    
    instance = None

    def __init__(self):
        self.instance = FastAPI()

    def run(self):
        self.instance.include_router(item_router)
        uvicorn.run(self.instance, port=8000)

    @staticmethod
    def get_instance():
        return API.instance
    
    @classmethod
    def startup_event(cls):
        print("startup fastapi")
        # Initialize your database or perform any other startup tasks here
        cls.instance.include_router(item_router)
        return cls.instance