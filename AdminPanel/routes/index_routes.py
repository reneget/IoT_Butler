from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from loguru import logger

from auth import require_auth

router: APIRouter = APIRouter()


@router.get("/")
@require_auth
async def index(request: Request) -> RedirectResponse:
    """
    Redirect to users page
    
    Args:
        request: FastAPI request object
        
    Returns:
        RedirectResponse to users page
    """
    logger.info('Request to index page, redirecting to users')
    return RedirectResponse(url="/users", status_code=303)

