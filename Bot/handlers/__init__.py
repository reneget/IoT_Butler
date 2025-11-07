from aiogram import Dispatcher
from .common import register_common_handlers
from .device import register_device_handlers


def register_handlers(dp: Dispatcher):
    """
    Register all handlers
    
    Args:
        dp: Dispatcher instance
    """
    register_common_handlers(dp)
    register_device_handlers(dp)

