from dataclasses import dataclass


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
    api: APIConfig
    auth: AuthConfig

