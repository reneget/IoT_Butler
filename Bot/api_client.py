import httpx
import logging
from typing import List, Dict, Any, Optional
from configurations import main_config
from datetime import datetime

api_logger: logging.Logger = logging.getLogger(__name__)


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
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by Telegram user_id
        
        Args:
            user_id: Telegram user_id of the user
            
        Returns:
            Dictionary with user data or None if not found
        """
        try:
            api_logger.info(f'Request to get user: user_id={user_id}')
            response = await self.client.get(f"{self.base_url}/user/get/user/{user_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            result = response.json()
            api_logger.info('User received')
            return result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                return None
            api_logger.error('Error getting user', exc_info=True)
            raise
        except Exception as e:
            api_logger.error('Error getting user', exc_info=True)
            raise
    
    async def create_user(self, user_id: int, tag: str) -> Dict[str, Any]:
        """
        Create a new user
        
        Args:
            user_id: Telegram user_id
            tag: Telegram username
            
        Returns:
            Dictionary with created user data
        """
        try:
            api_logger.info('Request to create a new user')
            user_data = {
                "user_id": user_id,
                "tag": tag,
                "create_time": datetime.now().isoformat()
            }
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
            raise
        except Exception as e:
            api_logger.error('An error occurred while creating the user', exc_info=True)
            raise
    
    # Device methods
    async def get_all_devices(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all devices for a user
        
        Args:
            user_id: Telegram user_id
            
        Returns:
            List of dictionaries with device data
        """
        try:
            api_logger.info(f'Request to get all devices for user: user_id={user_id}')
            response = await self.client.get(f"{self.base_url}/device/get/all/devices")
            response.raise_for_status()
            all_devices = response.json()
            
            # Get user to filter devices
            user = await self.get_user_by_id(user_id)
            if not user or not user.get('devices'):
                return []
            
            user_device_ids = user.get('devices', [])
            user_devices = [d for d in all_devices if d.get('device_id') in user_device_ids]
            api_logger.info(f'Found {len(user_devices)} devices for user')
            return user_devices
        except httpx.HTTPStatusError as e:
            api_logger.error('Error getting devices', exc_info=True)
            raise
        except Exception as e:
            api_logger.error('Error getting devices', exc_info=True)
            raise
    
    async def get_device_by_id(self, device_id: int) -> Optional[Dict[str, Any]]:
        """
        Get device by ID
        
        Args:
            device_id: ID of the device
            
        Returns:
            Dictionary with device data or None if not found
        """
        try:
            api_logger.info(f'Request to get device: device_id={device_id}')
            response = await self.client.get(f"{self.base_url}/device/get/device/{device_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            result = response.json()
            api_logger.info('Device received')
            return result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                return None
            api_logger.error('Error getting device', exc_info=True)
            raise
        except Exception as e:
            api_logger.error('Error getting device', exc_info=True)
            raise
    
    async def create_device(self, user_id: int, title: str, description: str, address: str) -> Dict[str, Any]:
        """
        Create a new device
        
        Args:
            user_id: Telegram user_id of the owner
            title: Device title
            description: Device description
            address: Device address
            
        Returns:
            Dictionary with created device data
        """
        try:
            api_logger.info('Request to create a new device')
            device_data = {
                "device_id": 0,  # Will be auto-generated
                "title": title,
                "description": description,
                "address": address,
                "create_time": datetime.now().isoformat()
            }
            response = await self.client.post(
                f"{self.base_url}/device/create/device",
                json=device_data
            )
            response.raise_for_status()
            device = response.json()
            
            # Add device to user's devices list
            user = await self.get_user_by_id(user_id)
            if user:
                devices = user.get('devices', [])
                devices.append(device['device_id'])
                device_counter = user.get('device_counter', 0) + 1
                
                update_data = {
                    "devices": devices,
                    "device_counter": device_counter
                }
                await self.client.put(
                    f"{self.base_url}/user/update/user/{user_id}",
                    json=update_data
                )
            
            api_logger.info('New device created')
            return device
        except httpx.HTTPStatusError as e:
            api_logger.error('An error occurred while creating the device', exc_info=True)
            raise
        except Exception as e:
            api_logger.error('An error occurred while creating the device', exc_info=True)
            raise
    
    async def update_device(self, device_id: int, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update device
        
        Args:
            device_id: ID of the device to update
            device_data: Dictionary with device data to update
            
        Returns:
            Dictionary with updated device data
        """
        try:
            api_logger.info(f'Device update request: device_id={device_id}')
            response = await self.client.put(
                f"{self.base_url}/device/update/device/{device_id}",
                json=device_data
            )
            response.raise_for_status()
            result = response.json()
            api_logger.info('Device updated')
            return result
        except httpx.HTTPStatusError as e:
            api_logger.error('Error updating device', exc_info=True)
            raise
        except Exception as e:
            api_logger.error('Error updating device', exc_info=True)
            raise
    
    async def delete_device(self, device_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete device and remove it from user's devices list
        
        Args:
            device_id: ID of the device to delete
            user_id: Telegram user_id of the owner
            
        Returns:
            Dictionary with deleted device data
        """
        try:
            api_logger.info(f'Request to delete device: device_id={device_id}')
            response = await self.client.delete(f"{self.base_url}/device/delete/device/{device_id}")
            response.raise_for_status()
            device = response.json()
            
            # Remove device from user's devices list
            user = await self.get_user_by_id(user_id)
            if user:
                devices = user.get('devices', [])
                if device_id in devices:
                    devices.remove(device_id)
                    device_counter = max(0, user.get('device_counter', 0) - 1)
                    
                    update_data = {
                        "devices": devices,
                        "device_counter": device_counter
                    }
                    await self.client.put(
                        f"{self.base_url}/user/update/user/{user_id}",
                        json=update_data
                    )
            
            api_logger.info('Device deleted')
            return device
        except httpx.HTTPStatusError as e:
            api_logger.error('Error deleting device', exc_info=True)
            raise
        except Exception as e:
            api_logger.error('Error deleting device', exc_info=True)
            raise

