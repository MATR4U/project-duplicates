import logging
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from database.DatabaseBase import DatabaseBase
from database.Postgresql import Postgresql

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

fast_api = FastAPI()

class APIServerUvicorn:
    _instance = None
    _initialized = False
    _db = None

    def __new__(cls, postgresql:Postgresql):
        if cls._instance is None:
            cls._instance = super(APIServerUvicorn, cls).__new__(cls)
        return cls._instance

    def __init__(self, postgresql:Postgresql):
        if hasattr(self, 'initialized') and self.initialized:
            logging.info("APIServer instance already initialized.")
            return

        try:
            logging.info("Initializing APIServer instance.")
            # self._setup_event_handlers()
            # self._setup_routes()
            # self._setup_exception_handlers()
            # Example database operation
            self._db = postgresql
            self._initialized = True
            logging.info("APIServer instance successfully initialized.")
        except Exception as e:
            logging.error(f"Error occurred during APIServer initialization: {e}", exc_info=True)
            raise

        @fast_api.on_event("startup")
        async def startup_event():
            logging.info("Starting FastAPI server...")

        @fast_api.on_event("shutdown")
        async def shutdown_event():
            logging.info("Shutting down FastAPI server...")


        @fast_api.get("/")
        async def read_root():
            results = self._db.execute("SELECT * FROM health_check")
            return {"message": str(results)}  # TODO message results: results)}


        @fast_api.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc):
            return JSONResponse(
                status_code=422,
                content={"error": "Validation Error", "detail": exc.errors()},
            )

        @fast_api.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request, exc):
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": "HTTP Exception", "detail": exc.detail},
            )


    def run(self, api_host, api_port, api_log_level):
        try:
            uvicorn.run("src.api.ApiServerUvicorn:fast_api", #main:fastApiApp
                        host=api_host,
                        port=api_port,
                        log_level=api_log_level,
                        reload=False  # TODO add into config
                        )
        except Exception as e:
            logging.error(f"An error occurred while running the fastapi server: {e}")
