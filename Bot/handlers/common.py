from loguru import logger
from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from api_client import APIClient


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
                await message.answer(
                    f"👋 Добро пожаловать в систему управления умным домом!\n\n"
                    f"Вы успешно зарегистрированы.\n\n"
                    f"Используйте /help для просмотра доступных команд."
                )
            else:
                # Check if user is banned
                if not user.get('active', True):
                    await message.answer(
                        "❌ Ваш аккаунт заблокирован. Обратитесь к администратору."
                    )
                    return
                
                await message.answer(
                    f"👋 С возвращением!\n\n"
                    f"Используйте /help для просмотра доступных команд."
                )
        
        # Show main menu
        await show_main_menu(message)
        
    except Exception as e:
        logger.error('Error in cmd_start', exc_info=True)
        await message.answer("❌ Произошла ошибка при регистрации. Попробуйте позже.")


async def cmd_help(message: Message):
    """
    Handle /help command - show available commands
    """
    help_text = (
        "📋 <b>Доступные команды:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/devices - Показать все ваши устройства\n"
        "/add_device - Добавить новое устройство\n"
        "/menu - Показать главное меню\n\n"
        "💡 Используйте кнопки меню для быстрого доступа к функциям."
    )
    await message.answer(help_text)


async def show_main_menu(message: Message):
    """
    Show main menu with inline keyboard
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Мои устройства", callback_data="list_devices")],
        [InlineKeyboardButton(text="➕ Добавить устройство", callback_data="add_device")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ])
    
    await message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )


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

