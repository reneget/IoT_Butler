import httpx
from typing import List, Dict, Any, Optional
from configurations import main_config
from fastapi import HTTPException
from loguru import logger as api_logger


class APIClient:
    """
    Client for interacting with Database API
    """
    
    def __init__(self) -> None:
        """
        Initialize API client with base URL and HTTP client
        """
        self.base_url: str = main_config.api.base_url
        self.client: httpx.AsyncClient = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self) -> "APIClient":
        """
        Async context manager entry
        
        Returns:
            APIClient instance
        """
        return self
    
    async def __aexit__(self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        """
        Async context manager exit
        
        Args:
            exc_type: Exception type if any
            exc_val: Exception value if any
            exc_tb: Exception traceback if any
        """
        await self.close()
    
    async def close(self) -> None:
        """
        Close the HTTP client
        """
        await self.client.aclose()
    
    # User methods
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users
        
        Returns:
            List of dictionaries with user data
            
        Raises:
            HTTPException: If request fails
        """
        try:
            api_logger.info('Request to get all users')
            response = await self.client.get(f"{self.base_url}/user/get/all/users")
            response.raise_for_status()
            result = response.json()
            api_logger.info('All users received')
            return result
        except httpx.HTTPStatusError as e:
            api_logger.error('Error getting all users', exc_info=True)
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            api_logger.error('Error getting all users', exc_info=True)
            raise
    
    async def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """
        Get user by ID
        
        Args:
            user_id: ID of the user to get
            
        Returns:
            Dictionary with user data
            
        Raises:
            HTTPException: If request fails
        """
        try:
            api_logger.info(f'Request to get user: user_id={user_id}')
            response = await self.client.get(f"{self.base_url}/user/get/user/{user_id}")
            response.raise_for_status()
            result = response.json()
            api_logger.info('User received')
            return result
        except httpx.HTTPStatusError as e:
            api_logger.error('Error getting user', exc_info=True)
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            api_logger.error('Error getting user', exc_info=True)
            raise
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user
        
        Args:
            user_data: Dictionary with user data to create
            
        Returns:
            Dictionary with created user data
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            api_logger.info('Request to create a new user')
            response = await self.client.post(
                f"{self.base_url}/user/create/user",
                json=user_data
            )
            response.raise_for_status()
            result = response.json()
            api_logger.info('New user created')
            return result
        except httpx.HTTPStatusError as e:
            api_logger.error('An error occurred while creating the user', exc_info=True)
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            api_logger.error('An error occurred while creating the user', exc_info=True)
            raise
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user
        
        Args:
            user_id: ID of the user to update
            user_data: Dictionary with user data to update
            
        Returns:
            Dictionary with updated user data
            
        Raises:
            HTTPException: If update fails
        """
        try:
            api_logger.info(f'User update request: user_id={user_id}')
            response = await self.client.put(
                f"{self.base_url}/user/update/user/{user_id}",
                json=user_data
            )
            response.raise_for_status()
            result = response.json()
            api_logger.info('User updated')
            return result
        except httpx.HTTPStatusError as e:
            api_logger.error('Error updating user', exc_info=True)
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            api_logger.error('Error updating user', exc_info=True)
            raise
    
    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        Delete user
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            Dictionary with deleted user data
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            api_logger.info(f'Request to delete user: user_id={user_id}')
            response = await self.client.delete(f"{self.base_url}/user/delete/user/{user_id}")
            response.raise_for_status()
            result = response.json()
            api_logger.info('User deleted')
            return result
        except httpx.HTTPStatusError as e:
            api_logger.error('Error deleting user', exc_info=True)
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            api_logger.error('Error deleting user', exc_info=True)
            raise
    

