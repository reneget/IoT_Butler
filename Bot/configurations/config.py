from dataclasses import dataclass
from typing import Optional, Dict, Tuple
from .env_conf import EnvConfig


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
class BotConfig:
    """
    Configuration class for Telegram Bot
    """
    token: str


@dataclass
class Config:
    """
    Main configuration class for whole project
    """
    loki: LokiConfig
    api: APIConfig
    bot: BotConfig


def load_config() -> Config:
    """
    Load configuration from environment variables
    
    Returns:
        Config object with all configuration
    """
    env = EnvConfig.read()
    
    return Config(
        loki=LokiConfig(
            url=env.str("LOKI_URL", default="http://loki:3100"),
            tags={"service": "bot"},
            auth=(env.str("LOKI_USER", default="admin"), env.str("LOKI_PASSWORD", default="admin")),
            version="1"
        ),
        api=APIConfig(
            base_url=env.str("API_BASE_URL", default="http://database:8000")
        ),
        bot=BotConfig(
            token=env.str("BOT_TOKEN", default="")
        )
    )


main_config = load_config()

