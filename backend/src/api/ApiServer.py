import logging
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.utils.Config import Config
from src.database.Base import DatabaseBase

# TODO cleanup imports
#from src.db.database import SessionLocal

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class APIServer:

    _instance = None
    app = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIServer, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Store the FastAPI app as an instance variable
        self.app = FastAPI()

        # Define an event handler for startup
        @self.app.on_event("startup")
        async def startup_event():
            print("Starting FastAPI server...")
            # You can print additional server details or setup tasks here

        # Define an event handler for shutdown
        @self.app.on_event("shutdown")
        async def shutdown_event():
            print("Shutting down FastAPI server...")
            # You can perform cleanup tasks here

        # Sample route
        @self.app.get("/")
        async def read_root():
            singleton = DatabaseBase()
            results = singleton.execute(str("SELECT * FROM health_check"))
            return {"message": str(results)}

        # Exception handler for RequestValidationError
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc):
            return JSONResponse(
                status_code=422,
                content={"error": "Validation Error", "detail": exc.errors()},
            )

        # Exception handler for HTTPException
        @self.app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request, exc):
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": "HTTP Exception", "detail": exc.detail},
            )

    def run(self):
        try:
            # Create an instance of Config (the singleton)
            conf = Config().get_config_api()
            #logging.info(f"Running server on {conf['host']}:{conf['port']} with log level {conf['log_level']}...")
            
            # TODO , reload=conf['reload']$
            # This argument, if set to True, enables auto-reloading of your FastAPI application when code changes are detected. During development, this is useful to automatically restart the server when you make code modifications. 
            uvicorn.run(self.app, host=conf['api_host'], port=conf['api_port'], log_level=conf['api_log_level'])
        except Exception as e:
            """
            Log any exceptions that occur while running the fastapi server
            """
            logging.error(f"An error occurred while running the fastapi server: {e}")
