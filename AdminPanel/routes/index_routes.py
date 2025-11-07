from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import logging

from auth import require_auth

router: APIRouter = APIRouter()
logger: logging.Logger = logging.getLogger(__name__)


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

