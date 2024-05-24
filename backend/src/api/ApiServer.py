import logging
import uvicorn

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
            # self._setup_event_handlers()
            # self._setup_routes()
            # self._setup_exception_handlers()
            self.initialized = True
            logging.info("APIServer instance successfully initialized.")
        except Exception as e:
            logging.error(f"Error occurred during APIServer initialization: {e}", exc_info=True)
            raise

    def run(self, api_host, api_port, api_log_level):
        try:
            uvicorn.run("src.api.FastApiHandler:fast_api", #main:fastApiApp
                        host=api_host,
                        port=api_port,
                        log_level=api_log_level,
                        reload=False  # TODO add into config
                        )
        except Exception as e:
            logging.error(f"An error occurred while running the fastapi server: {e}")
