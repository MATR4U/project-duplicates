from fastapi import FastAPI, APIRouter
from typing import List, Tuple


class RouterBase:
    def __init__(self, app: FastAPI, prefix: str = "/api/v1"):
        self.app = app
        self.prefix = prefix

    def include_routers(self, routers: List[Tuple[APIRouter, str]]):
        """
        Include a list of routers in the FastAPI application.

        :param routers: List of tuples, each containing an APIRouter instance and its specific path.
        """
        for router, path in routers:
            self.app.include_router(router, prefix=self.prefix + path)
