from fastapi import FastAPI
import uvicorn

import API
from DataBase.core.db_connection import create_tables
from log.config import logger

logger.info('Creating Tables')
create_tables()
logger.info('Tables created')

app = FastAPI()
logger.info('FastAPI object initialized')

logger.info('Connecting routers')
app.include_router(API.user_router)
app.include_router(API.device_router)
logger.info('Routers are connected')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
