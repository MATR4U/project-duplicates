
import logging
import uvicorn
from fastapi import FastAPI
from src.api.routers.item_router import router as item_router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class API:
    
    instance = None

    def __init__(self):
        self.instance = FastAPI()

    def run(self):
        self.instance.include_router(item_router)
        uvicorn.run(self.instance, port=8000)