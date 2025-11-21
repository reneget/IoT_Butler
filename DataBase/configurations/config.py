from dataclasses import dataclass


@dataclass
class DBConfig:
    """
    Configuration class for DataBase
    """
    db_url: str


@dataclass
class Config:
    """
    Main configuration class for whole project
    """
    db: DBConfig
