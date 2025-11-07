from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Any, Union
from datetime import datetime
import logging

from auth import require_auth
from api_client import APIClient
from validation import validate_user_id

router: APIRouter = APIRouter()
templates: Jinja2Templates = Jinja2Templates(directory="templates")
logger: logging.Logger = logging.getLogger(__name__)


@router.get("/users", response_class=HTMLResponse)
@require_auth
async def users_page(request: Request) -> HTMLResponse:
    """
    Users management page
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTMLResponse with users page
    """
    try:
        logger.info('Request to get users page')
        async with APIClient() as client:
            users: List[Dict[str, Any]] = await client.get_all_users()
        logger.info('Users page loaded successfully')
        return templates.TemplateResponse(
            "users.html",
            {"request": request, "users": users, "active_tab": "users"}
        )
    except HTTPException as e:
        logger.error('HTTP error loading users page', exc_info=True)
        return templates.TemplateResponse(
            "users.html",
            {"request": request, "users": [], "error": f"Ошибка при загрузке данных: {e.detail}", "active_tab": "users"},
            status_code=e.status_code
        )
    except Exception as e:
        logger.error('Error loading users page', exc_info=True)
        return templates.TemplateResponse(
            "users.html",
            {"request": request, "users": [], "error": "Произошла ошибка при загрузке страницы пользователей.", "active_tab": "users"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/users/update/{user_id}", response_model=None)
@require_auth
async def update_user(request: Request, user_id: int) -> Union[RedirectResponse, HTMLResponse]:
    """
    Update user - only ban (active) field
    
    Args:
        request: FastAPI request object
        user_id: Telegram user_id (unique identifier) of the user to update
        
    Returns:
        RedirectResponse to users page
    """
    # Validate user_id
    is_valid, error_message, validated_id = validate_user_id(user_id)
    if not is_valid:
        logger.warning(f'User update failed validation: user_id={user_id}, error={error_message}')
        async with APIClient() as client:
            users: List[Dict[str, Any]] = await client.get_all_users()
        return templates.TemplateResponse(
            "users.html",
            {"request": request, "users": users, "error": error_message, "active_tab": "users"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    form_data = await request.form()
    
    try:
        logger.info(f'User update request: user_id={user_id}')
        # ban checkbox: if checked (present in form_data with value "on"), active=False
        # When checkbox is unchecked, "ban" key is not in form_data, so active=True
        ban_checked: bool = "ban" in form_data and form_data.get("ban") == "on"
        user_data: Dict[str, bool] = {
            "active": not ban_checked
        }
        
        async with APIClient() as client:
            await client.update_user(validated_id, user_data)
        logger.info('User updated')
        return RedirectResponse(url="/users", status_code=303)
    except HTTPException as e:
        logger.error('Error updating user', exc_info=True)
        async with APIClient() as client:
            users: List[Dict[str, Any]] = await client.get_all_users()
        return templates.TemplateResponse(
            "users.html",
            {"request": request, "users": users, "error": f"Ошибка при обновлении пользователя: {e.detail}", "active_tab": "users"},
            status_code=e.status_code
        )
    except Exception as e:
        logger.error('Error updating user', exc_info=True)
        async with APIClient() as client:
            users: List[Dict[str, Any]] = await client.get_all_users()
        return templates.TemplateResponse(
            "users.html",
            {"request": request, "users": users, "error": "Произошла ошибка при обновлении пользователя.", "active_tab": "users"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

