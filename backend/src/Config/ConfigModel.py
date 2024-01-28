from pydantic import BaseModel, Field, HttpUrl
import json
from typing import Optional


class DatabaseConfig(BaseModel):
    db_type: Optional[str]
    db_user: Optional[str]
    db_password: Optional[str]
    db_host: Optional[str]
    db_port: Optional[str]
    db_name: Optional[str]


class APIConfig(BaseModel):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_log_level: str = "info"


class AppConfig(BaseModel):
    source: Optional[str]
    destination: Optional[str]
    batch_size: Optional[int]
    api_endpoint: Optional[str]
    api_token: Optional[str]
    Database: Optional[DatabaseConfig]
    API: Optional[APIConfig]


class ArgsConfig(BaseModel):
    source: Optional[str] = None
    destination: Optional[str] = None
    batch_size: Optional[int] = None
    api_endpoint: Optional[HttpUrl] = None
    api_token: Optional[str] = None
    db_url: Optional[str] = None


def load_config(file_path: str) -> AppConfig:
    # Read JSON file
    with open(file_path, 'r') as file:
        config_data = json.load(file)

    # Validate individual configurations
    # AppConfig.model_validate_json(**config_data)
    app_config = AppConfig(**config_data)

    return AppConfig(app=app_config)
