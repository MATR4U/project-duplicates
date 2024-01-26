import logging
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from Config.ConfigurationModel import AppConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class APIServer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIServer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized') and self.initialized:
            logging.info("APIServer instance already initialized.")
            return

        try:
            logging.info("Initializing APIServer instance.")
            self.fast_api = FastAPI()
            self._setup_event_handlers()
            self._setup_routes()
            self._setup_exception_handlers()
            self.initialized = True
            logging.info("APIServer instance successfully initialized.")
        except Exception as e:
            logging.error(f"Error occurred during APIServer initialization: {e}", exc_info=True)
            raise

    def _setup_event_handlers(self):
        @self.fast_api.on_event("startup")
        async def startup_event():
            logging.info("Starting FastAPI server...")

        @self.fast_api.on_event("shutdown")
        async def shutdown_event():
            logging.info("Shutting down FastAPI server...")

    def _setup_routes(self):
        @self.fast_api.get("/")
        async def read_root():
            # Example database operation
            from database.DatabaseBase import DatabaseBase
            singleton = DatabaseBase()
            results = singleton.execute("SELECT * FROM health_check")
            return {"message": str("")}  # results)}

    def _setup_exception_handlers(self):
        @self.fast_api.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc):
            return JSONResponse(
                status_code=422,
                content={"error": "Validation Error", "detail": exc.errors()},
            )

        @self.fast_api.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request, exc):
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": "HTTP Exception", "detail": exc.detail},
            )

    def run(self, config: AppConfig):
        try:
            uvicorn.run(self.fast_api,
                        host=config.API.api_host,
                        port=config.API.api_port,
                        log_level=config.API.api_log_level)
        except Exception as e:
            logging.error(f"An error occurred while running the fastapi server: {e}")
