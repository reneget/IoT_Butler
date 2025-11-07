"""
Validation functions for admin panel data
"""
import re
import logging
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse

validation_logger: logging.Logger = logging.getLogger(__name__)


def validate_string_field(value: Optional[str], field_name: str, required: bool = False, 
                         max_length: Optional[int] = None, min_length: Optional[int] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate string field
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        required: Whether field is required
        max_length: Maximum length
        min_length: Minimum length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        value = ""
    
    value = str(value).strip()
    
    if required and not value:
        return False, f"Поле '{field_name}' обязательно для заполнения"
    
    if value and min_length and len(value) < min_length:
        return False, f"Поле '{field_name}' должно содержать минимум {min_length} символов"
    
    if value and max_length and len(value) > max_length:
        return False, f"Поле '{field_name}' должно содержать максимум {max_length} символов"
    
    return True, None


def validate_url(value: Optional[str], field_name: str, required: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate URL field
    
    Args:
        value: URL to validate
        field_name: Name of the field for error messages
        required: Whether field is required
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value or not value.strip():
        if required:
            return False, f"Поле '{field_name}' обязательно для заполнения"
        return True, None
    
    value = value.strip()
    
    # Basic URL validation
    try:
        result = urlparse(value)
        if not all([result.scheme, result.netloc]):
            if not value.startswith('http://') and not value.startswith('https://'):
                return False, f"Поле '{field_name}' должно быть валидным URL (начинаться с http:// или https://)"
    except Exception:
        return False, f"Поле '{field_name}' содержит некорректный URL"
    
    return True, None


def validate_position_id(position_id: Any) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Validate position ID
    
    Args:
        position_id: Position ID to validate
        
    Returns:
        Tuple of (is_valid, error_message, validated_id)
    """
    try:
        pos_id = int(position_id)
        if pos_id <= 0:
            return False, "ID позиции должен быть положительным числом", None
        return True, None, pos_id
    except (ValueError, TypeError):
        return False, "ID позиции должен быть числом", None


def validate_user_id(user_id: Any) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Validate user ID (Telegram ID)
    
    Args:
        user_id: User ID to validate
        
    Returns:
        Tuple of (is_valid, error_message, validated_id)
    """
    try:
        uid = int(user_id)
        if uid <= 0:
            return False, "ID пользователя должен быть положительным числом", None
        return True, None, uid
    except (ValueError, TypeError):
        return False, "ID пользователя должен быть числом", None


def validate_position_data(position_data: Dict[str, Any], is_update: bool = False) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Validate position data
    
    Args:
        position_data: Position data dictionary
        is_update: Whether this is an update operation
        
    Returns:
        Tuple of (is_valid, error_message, validated_data)
    """
    validated_data: Dict[str, Any] = {}
    
    # Validate brand
    if "brand" in position_data:
        is_valid, error = validate_string_field(
            position_data.get("brand"), 
            "Бренд", 
            required=not is_update,
            max_length=200
        )
        if not is_valid:
            return False, error, {}
        validated_data["brand"] = str(position_data.get("brand")).strip()
    
    # Validate model
    if "model" in position_data:
        is_valid, error = validate_string_field(
            position_data.get("model"), 
            "Модель", 
            required=not is_update,
            max_length=200
        )
        if not is_valid:
            return False, error, {}
        validated_data["model"] = str(position_data.get("model")).strip()
    
    # Validate sizes
    if "sizes" in position_data:
        is_valid, error = validate_string_field(
            position_data.get("sizes"), 
            "Размеры", 
            required=not is_update,
            max_length=500
        )
        if not is_valid:
            return False, error, {}
        validated_data["sizes"] = str(position_data.get("sizes")).strip()
    
    # Validate image URL
    if "image" in position_data:
        image_value = position_data.get("image") or ""
        if image_value:
            is_valid, error = validate_url(image_value, "Изображение", required=False)
            if not is_valid:
                return False, error, {}
        validated_data["image"] = str(image_value).strip()
    
    # Validate description
    if "description" in position_data:
        is_valid, error = validate_string_field(
            position_data.get("description"), 
            "Описание", 
            required=False,
            max_length=2000
        )
        if not is_valid:
            return False, error, {}
        validated_data["description"] = str(position_data.get("description") or "").strip()
    
    # Validate avito_url
    if "avito_url" in position_data:
        avito_value = position_data.get("avito_url")
        if avito_value:
            is_valid, error = validate_url(avito_value, "Avito URL", required=False)
            if not is_valid:
                return False, error, {}
            validated_data["avito_url"] = str(avito_value).strip()
        else:
            validated_data["avito_url"] = None
    
    # Validate active status
    if "active" in position_data:
        active_value = position_data.get("active")
        if isinstance(active_value, bool):
            validated_data["active"] = active_value
        elif isinstance(active_value, str):
            validated_data["active"] = active_value.lower() in ('true', '1', 'on', 'yes')
        else:
            validated_data["active"] = bool(active_value)
    
    return True, None, validated_data


def sanitize_input(value: Any) -> str:
    """
    Sanitize input to prevent XSS and injection attacks
    
    Args:
        value: Value to sanitize
        
    Returns:
        Sanitized string
    """
    if value is None:
        return ""
    
    value = str(value)
    # Remove potentially dangerous characters
    value = value.replace('<', '&lt;').replace('>', '&gt;')
    value = value.replace('"', '&quot;').replace("'", '&#x27;')
    return value.strip()

