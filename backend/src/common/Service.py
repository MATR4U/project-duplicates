from fastapi import Depends

from database.DatabaseBase import DatabaseBase


# Assuming you have a service class
class MyService:
    def __init__(self, db: DatabaseBase):
        self.db = db

    # Dependency provider function
    def get_my_service(db: DatabaseBase = Depends(DatabaseBase)):
        return MyService(db)