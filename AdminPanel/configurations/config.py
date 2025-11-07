from dataclasses import dataclass
from typing import Optional, Dict, Tuple


@dataclass
class LokiConfig:
    """
    Configuration class for Loki logger
    """
    url: str
    tags: Optional[Dict[str, str]] = None
    auth: Optional[Tuple[str, str]] = ('admin', 'admin')
    version: str = '1'


@dataclass
class APIConfig:
    """
    Configuration class for Database API
    """
    base_url: str


@dataclass
class AuthConfig:
    """
    Configuration class for authentication
    """
    secret_key: str
    username: str
    password: str


@dataclass
class Config:
    """
    Main configuration class for whole project
    """
    loki: LokiConfig
    api: APIConfig
    auth: AuthConfig

