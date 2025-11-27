from dataclasses import dataclass
from .env_conf import EnvConfig


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
    device_control_url: str | None = None


@dataclass
class Config:
    """
    Main configuration class for whole project
    """
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
        api=APIConfig(
            base_url=env.str("API_BASE_URL", default="http://database:8000")
        ),
        bot=BotConfig(
            token=env.str("BOT_TOKEN", default=""),
            device_control_url=env.str("DEVICE_CONTROL_URL", default="").strip() or None
        )
    )


main_config = load_config()

