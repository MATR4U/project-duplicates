from database.DatabaseBase import DatabaseBase
from sqlmodel import SQLModel, create_engine, Session
from src.common.Config import Config


class Postgresql(DatabaseBase):

    def __init__(self, config: Config):
        super().__init__(config)
