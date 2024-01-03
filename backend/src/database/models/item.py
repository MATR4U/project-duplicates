from sqlmodel import SQLModel, Field
from typing import Optional

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)  # Assuming 'name' should be non-nullable
    description: str = Field(default="")  # Defaulting 'description' to an empty string if not provided

# If you want 'description' to be nullable (i.e., it can be None), you can use:
# description: Optional[str] = Field(default=None, nullable=True)
