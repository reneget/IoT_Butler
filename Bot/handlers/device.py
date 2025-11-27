from loguru import logger
from aiogram import Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, User as TelegramUser
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from api_client import APIClient
from lexicon import LEXICON, BUTTONS, STATUS_LABELS


class DeviceStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_address = State()


async def _ensure_user_exists(client: APIClient, telegram_user: TelegramUser):
    """
    Make sure the user exists in the backend; create automatically if missing.
    """
    user = await client.get_user_by_id(telegram_user.id)
    if not user:
        username = telegram_user.username or f"user_{telegram_user.id}"
        user = await client.create_user(telegram_user.id, username)
    return user


async def cmd_devices(message: Message):
    """
    Handle /devices command - show all user devices
    """
    await list_devices_handler(message)


async def list_devices_callback(callback: CallbackQuery):
    """
    Handle callback for listing devices
    """
    await callback.answer()
    await list_devices_handler(callback.message, callback.from_user)


async def list_devices_handler(message: Message, telegram_user: TelegramUser | None = None):
    """
    List all devices for the user
    """
    try:
        telegram_user = telegram_user or message.from_user
        user_id = telegram_user.id
        
        async with APIClient() as client:
            user = await _ensure_user_exists(client, telegram_user)
            
            if not user.get('active', True):
                await message.answer(LEXICON["account_blocked"])
                return
            
            devices = await client.get_all_devices(user_id)
            
            if not devices:
                await message.answer(LEXICON["no_devices"])
                return
            
            text = LEXICON["devices_list_header"]
            keyboard_buttons = []
            
            for device in devices:
                device_id = device.get('device_id')
                title = device.get('title', STATUS_LABELS["title_unknown"])
                description = device.get('description', '')
                active = device.get('active', False)
                status = STATUS_LABELS["on"] if active else STATUS_LABELS["off"]
                
                text += f"<b>{title}</b>\n"
                text += f"ID: {device_id}\n"
                if description:
                    text += f"Описание: {description}\n"
                text += f"Статус: {status}\n"
                text += f"Адрес: {device.get('address', STATUS_LABELS['address_unknown'])}\n"
                text += "─" * 20 + "\n"
                
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"{title} ({STATUS_LABELS['icon_on'] if active else STATUS_LABELS['icon_off']})",
                        callback_data=f"device_{device_id}"
                    )
                ])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons + [
                [InlineKeyboardButton(text=BUTTONS["add_device"], callback_data="add_device")],
                [InlineKeyboardButton(text=BUTTONS["main_menu"], callback_data="main_menu")]
            ])
            
            await message.answer(text, reply_markup=keyboard)
            
    except Exception as e:
        logger.error('Error listing devices', exc_info=True)
        await message.answer(LEXICON["list_devices_error"])


async def add_device_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handle callback for adding device
    """
    await callback.answer()
    await add_device_start(callback.message, state, callback.from_user)


async def add_device_start(message: Message, state: FSMContext, telegram_user: TelegramUser | None = None):
    """
    Start adding device process
    """
    try:
        telegram_user = telegram_user or message.from_user
        
        async with APIClient() as client:
            user = await _ensure_user_exists(client, telegram_user)
            if not user.get('active', True):
                await message.answer(LEXICON["account_blocked"])
                return
        
        await state.set_state(DeviceStates.waiting_for_title)
        await message.answer(LEXICON["add_device_intro"])
    except Exception as e:
        logger.error('Error starting add device', exc_info=True)
        await message.answer(LEXICON["add_device_error"])


async def process_title(message: Message, state: FSMContext):
    """
    Process device title
    """
    title = message.text.strip()
    if not title or len(title) > 100:
        await message.answer(LEXICON["invalid_title"])
        return
    
    await state.update_data(title=title)
    await state.set_state(DeviceStates.waiting_for_description)
    await message.answer(LEXICON["ask_description"])


async def process_description(message: Message, state: FSMContext):
    """
    Process device description
    """
    description = message.text.strip()
    if len(description) > 500:
        await message.answer(LEXICON["invalid_description"])
        return
    
    await state.update_data(description=description)
    await state.set_state(DeviceStates.waiting_for_address)
    await message.answer(LEXICON["ask_address"])


async def process_address(message: Message, state: FSMContext):
    """
    Process device address and create device
    """
    address = message.text.strip()
    if not address or len(address) > 200:
        await message.answer(LEXICON["invalid_address"])
        return
    
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        
        async with APIClient() as client:
            device = await client.create_device(
                user_id=user_id,
                title=data['title'],
                description=data.get('description', ''),
                address=address
            )
        
        await state.clear()
        await message.answer(
            LEXICON["device_added"].format(
                title=device.get('title'),
                device_id=device.get('device_id'),
                address=device.get('address')
            )
        )
        
    except Exception as e:
        logger.error('Error creating device', exc_info=True)
        await message.answer(LEXICON["create_device_error"])
        await state.clear()


async def device_action_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handle callback for device actions
    """
    await callback.answer()
    
    try:
        device_id = int(callback.data.split('_')[1])
        telegram_user = callback.from_user
        user_id = telegram_user.id
        
        async with APIClient() as client:
            device = await client.get_device_by_id(device_id)
            if not device:
                await callback.message.answer(LEXICON["device_not_found"])
                return
            
            # Check if device belongs to user
            user = await _ensure_user_exists(client, telegram_user)
            if not user or device_id not in user.get('devices', []):
                await callback.message.answer(LEXICON["no_device_access"])
                return
            
            active = device.get('active', False)
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=STATUS_LABELS["toggle_on"] if not active else STATUS_LABELS["toggle_off"],
                        callback_data=f"toggle_{device_id}"
                    )
                ],
                [InlineKeyboardButton(text=BUTTONS["delete_device"], callback_data=f"delete_{device_id}")],
                [InlineKeyboardButton(text=BUTTONS["back_to_devices"], callback_data="list_devices")]
            ])
            
            await callback.message.answer(
                f"<b>{device.get('title')}</b>\n\n"
                f"ID: {device_id}\n"
                f"Описание: {device.get('description', STATUS_LABELS['description_unknown'])}\n"
                f"Адрес: {device.get('address', STATUS_LABELS['address_unknown'])}\n"
                f"Статус: {STATUS_LABELS['on'] if active else STATUS_LABELS['off']}\n"
                f"Создано: {device.get('create_time', STATUS_LABELS['created_unknown'])}",
                reply_markup=keyboard
            )
            
    except Exception as e:
        logger.error('Error in device action callback', exc_info=True)
        await callback.message.answer(LEXICON["generic_error"])


async def toggle_device_callback(callback: CallbackQuery):
    """
    Handle toggle device callback
    """
    await callback.answer()
    
    try:
        device_id = int(callback.data.split('_')[1])
        telegram_user = callback.from_user
        user_id = telegram_user.id
        
        async with APIClient() as client:
            device = await client.get_device_by_id(device_id)
            if not device:
                await callback.message.answer(LEXICON["device_not_found"])
                return
            
            user = await _ensure_user_exists(client, telegram_user)
            if not user or device_id not in user.get('devices', []):
                await callback.message.answer(LEXICON["no_device_access"])
                return
            
            # Toggle device
            new_active = not device.get('active', False)
            await client.update_device(device_id, {"active": new_active})
            
            updated_device = await client.get_device_by_id(device_id)
            if updated_device:
                await client.send_device_packet(updated_device)

            status_text = STATUS_LABELS["text_on"] if new_active else STATUS_LABELS["text_off"]
            await callback.message.answer(
                LEXICON["device_toggle_success"].format(status=status_text)
            )
            
            # Update the device list
            await list_devices_handler(callback.message, callback.from_user)
            
    except Exception as e:
        logger.error('Error toggling device', exc_info=True)
        await callback.message.answer(LEXICON["toggle_error"])


async def delete_device_callback(callback: CallbackQuery):
    """
    Handle delete device callback
    """
    await callback.answer()
    
    try:
        device_id = int(callback.data.split('_')[1])
        telegram_user = callback.from_user
        user_id = telegram_user.id
        
        async with APIClient() as client:
            device = await client.get_device_by_id(device_id)
            if not device:
                await callback.message.answer(LEXICON["device_not_found"])
                return
            
            user = await _ensure_user_exists(client, telegram_user)
            if not user or device_id not in user.get('devices', []):
                await callback.message.answer(LEXICON["no_device_access"])
                return
            
            await client.delete_device(device_id, user_id)
            await callback.message.answer(
                LEXICON["device_deleted"].format(title=device.get('title'))
            )
            
            # Update the device list
            await list_devices_handler(callback.message, callback.from_user)
            
    except Exception as e:
        logger.error('Error deleting device', exc_info=True)
        await callback.message.answer(LEXICON["delete_error"])


async def help_callback(callback: CallbackQuery):
    """
    Handle help callback
    """
    await callback.answer()
    await callback.message.answer(LEXICON["help_text"])


async def main_menu_callback(callback: CallbackQuery):
    """
    Handle main menu callback
    """
    await callback.answer()
    from .common import show_main_menu
    await show_main_menu(callback.message)


def register_device_handlers(dp: Dispatcher):
    """
    Register device handlers
    
    Args:
        dp: Dispatcher instance
    """
    # Commands
    dp.message.register(cmd_devices, Command("devices"))
    dp.message.register(add_device_start, Command("add_device"), StateFilter(None))
    
    # Callbacks
    dp.callback_query.register(list_devices_callback, F.data == "list_devices")
    dp.callback_query.register(add_device_callback, F.data == "add_device")
    dp.callback_query.register(device_action_callback, F.data.startswith("device_"))
    dp.callback_query.register(toggle_device_callback, F.data.startswith("toggle_"))
    dp.callback_query.register(delete_device_callback, F.data.startswith("delete_"))
    dp.callback_query.register(help_callback, F.data == "help")
    dp.callback_query.register(main_menu_callback, F.data == "main_menu")
    
    # FSM handlers
    dp.message.register(process_title, DeviceStates.waiting_for_title)
    dp.message.register(process_description, DeviceStates.waiting_for_description)
    dp.message.register(process_address, DeviceStates.waiting_for_address)

