from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Health(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    service: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)