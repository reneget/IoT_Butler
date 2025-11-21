from . import config as cf
from .env_conf import EnvConfig

env = EnvConfig.read()

main_config = cf.Config(
    api=cf.APIConfig(
        base_url=env('API_BASE_URL', default='http://database:8000')
    ),
    auth=cf.AuthConfig(
        secret_key=env('SECRET_KEY', default="secret_key2112"),
        username=env('ADMIN_USERNAME', default='admin'),
        password=env('ADMIN_PASSWORD', default='admin')
    )
)
