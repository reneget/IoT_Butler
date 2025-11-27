from loguru import logger
from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from api_client import APIClient
from lexicon import LEXICON, BUTTONS


async def cmd_start(message: Message):
    """
    Handle /start command - register user and show main menu
    """
    try:
        user_id = message.from_user.id
        username = message.from_user.username or f"user_{user_id}"
        
        logger.info(f'User {user_id} started the bot')
        
        async with APIClient() as client:
            # Check if user exists
            user = await client.get_user_by_id(user_id)
            
            if not user:
                # Create new user
                user = await client.create_user(user_id, username)
                await message.answer(LEXICON["start_new_user"])
            else:
                # Check if user is banned
                if not user.get('active', True):
                    await message.answer(LEXICON["start_banned"])
                    return
                
                await message.answer(LEXICON["start_returning"])
        
        # Show main menu
        await show_main_menu(message)
        
    except Exception as e:
        logger.error('Error in cmd_start', exc_info=True)
        await message.answer(LEXICON["start_error"])


async def cmd_help(message: Message):
    """
    Handle /help command - show available commands
    """
    await message.answer(LEXICON["help_text"])


async def show_main_menu(message: Message):
    """
    Show main menu with inline keyboard
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTONS["list_devices"], callback_data="list_devices")],
        [InlineKeyboardButton(text=BUTTONS["add_device"], callback_data="add_device")],
        [InlineKeyboardButton(text=BUTTONS["help"], callback_data="help")]
    ])
    
    await message.answer(LEXICON["main_menu"], reply_markup=keyboard)


async def cmd_menu(message: Message):
    """
    Handle /menu command - show main menu
    """
    await show_main_menu(message)


def register_common_handlers(dp: Dispatcher):
    """
    Register common handlers
    
    Args:
        dp: Dispatcher instance
    """
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_menu, Command("menu"))

