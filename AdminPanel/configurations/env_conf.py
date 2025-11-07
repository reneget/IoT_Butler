from environs import Env
from typing import Any


class EnvConfig:
    """
    Configuration class for reading environment variables
    """
    
    @staticmethod
    def read() -> Env:
        """
        Read environment variables from .env file
        
        Returns:
            Env object with loaded environment variables
        """
        env: Env = Env()
        env.read_env()

        return env
