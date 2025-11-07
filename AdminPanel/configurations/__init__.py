from . import config as cf
from .env_conf import EnvConfig

env = EnvConfig.read()

main_config = cf.Config(
    loki=cf.LokiConfig(
        url=env('LOKI_URL', default="http://loki:3100/loki/api/v1/push"),
    ),
    api=cf.APIConfig(
        base_url=env('API_BASE_URL', default='http://database:8000')
    ),
    auth=cf.AuthConfig(
        secret_key=env('SECRET_KEY', default="secret_key2112"),
        username=env('ADMIN_USERNAME', default='admin'),
        password=env('ADMIN_PASSWORD', default='admin')
    )
)
