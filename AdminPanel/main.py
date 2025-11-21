from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from configurations import main_config
from routes import auth_routes, user_routes, index_routes
from log.config import logger

app = FastAPI(title="Admin Panel")

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=main_config.auth.secret_key,
    max_age=3600,  # 1 hour
    same_site="lax"
)

# Include routers
app.include_router(index_routes.router)
app.include_router(auth_routes.router)
app.include_router(user_routes.router)

logger.info("Admin Panel initialized")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

