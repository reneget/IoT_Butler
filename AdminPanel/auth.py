from fastapi import Request
from fastapi.security import HTTPBasic
from starlette.responses import RedirectResponse
from functools import wraps
from typing import Callable, Any, Awaitable
import secrets
import logging

from configurations import main_config

auth_logger: logging.Logger = logging.getLogger(__name__)
security: HTTPBasic = HTTPBasic()


def is_ascii(text: str) -> bool:
    """
    Check if string contains only ASCII characters
    
    Args:
        text: String to check
        
    Returns:
        True if string contains only ASCII characters, False otherwise
    """
    try:
        text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def verify_credentials(username: str, password: str) -> bool:
    """
    Verify admin credentials
    
    Args:
        username: Username to verify
        password: Password to verify
        
    Returns:
        True if credentials are valid, False otherwise
        
    Raises:
        ValueError: If credentials contain non-ASCII characters
    """
    # Check for ASCII-only characters
    if not is_ascii(username) or not is_ascii(password):
        auth_logger.warning('Login attempt with non-ASCII characters in credentials')
        raise ValueError("Логин и пароль должны содержать только латинские буквы, цифры и стандартные символы")
    
    try:
        return (
            secrets.compare_digest(username, main_config.auth.username) and
            secrets.compare_digest(password, main_config.auth.password)
        )
    except TypeError as e:
        # Fallback to regular comparison if compare_digest fails (shouldn't happen after ASCII check)
        auth_logger.error(f'Error comparing credentials: {e}', exc_info=True)
        return (
            username == main_config.auth.username and
            password == main_config.auth.password
        )


def require_auth(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """
    Decorator to require authentication
    
    Args:
        func: Function to wrap with authentication check
        
    Returns:
        Wrapped function that checks authentication before execution
    """
    @wraps(func)
    async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
        if not request.session.get("authenticated"):
            return RedirectResponse(url="/login", status_code=303)
        return await func(request, *args, **kwargs)
    return wrapper

