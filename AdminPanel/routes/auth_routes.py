from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Union
from loguru import logger

from auth import verify_credentials
from configurations import main_config

router: APIRouter = APIRouter()
templates: Jinja2Templates = Jinja2Templates(directory="templates")


@router.get("/login", response_model=None)
async def login_page(request: Request) -> Union[HTMLResponse, RedirectResponse]:
    """
    Login page
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTMLResponse with login page or RedirectResponse if already authenticated
    """
    if request.session.get("authenticated"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_model=None)
async def login(request: Request, username: str = Form(...), password: str = Form(...)) -> Union[HTMLResponse, RedirectResponse]:
    """
    Handle login
    
    Args:
        request: FastAPI request object
        username: Username from form
        password: Password from form
        
    Returns:
        RedirectResponse to main page on success, HTMLResponse with error on failure
    """
    try:
        logger.info('Login attempt')
        # Sanitize inputs
        username = username.strip() if username else ""
        password = password.strip() if password else ""
        
        # Basic validation
        if not username or not password:
            logger.warning('Login failed: empty username or password')
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Логин и пароль обязательны для заполнения"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Check credentials
        try:
            if verify_credentials(username, password):
                request.session["authenticated"] = True
                logger.info('User logged in successfully')
                return RedirectResponse(url="/", status_code=303)
            else:
                logger.warning('Login failed: invalid credentials')
                return templates.TemplateResponse(
                    "login.html",
                    {"request": request, "error": "Неверный логин или пароль"},
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
        except ValueError as e:
            # Handle non-ASCII characters error
            logger.warning(f'Login failed: {str(e)}')
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error('Error during login', exc_info=True)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Произошла ошибка при входе. Попробуйте еще раз."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    """
    Handle logout
    
    Args:
        request: FastAPI request object
        
    Returns:
        RedirectResponse to login page
    """
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

