import logging
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


fast_api = FastAPI()


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
        singleton = DatabaseBase()  # implemented None to remove warning accessing Singleton
        results = singleton.execute("SELECT * FROM health_check")
        return {"message": str("")}  # TODO message results: results)}


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
