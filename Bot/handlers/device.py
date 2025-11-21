from loguru import logger
from aiogram import Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from api_client import APIClient


class DeviceStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_address = State()


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
    await list_devices_handler(callback.message)


async def list_devices_handler(message: Message):
    """
    List all devices for the user
    """
    try:
        user_id = message.from_user.id
        
        async with APIClient() as client:
            # Check if user exists and is active
            user = await client.get_user_by_id(user_id)
            if not user:
                await message.answer("❌ Вы не зарегистрированы. Используйте /start")
                return
            
            if not user.get('active', True):
                await message.answer("❌ Ваш аккаунт заблокирован.")
                return
            
            devices = await client.get_all_devices(user_id)
            
            if not devices:
                await message.answer(
                    "📱 <b>Ваши устройства</b>\n\n"
                    "У вас пока нет устройств.\n"
                    "Используйте /add_device для добавления нового устройства."
                )
                return
            
            text = "📱 <b>Ваши устройства:</b>\n\n"
            keyboard_buttons = []
            
            for device in devices:
                device_id = device.get('device_id')
                title = device.get('title', 'Без названия')
                description = device.get('description', '')
                active = device.get('active', False)
                status = "🟢 Включено" if active else "🔴 Выключено"
                
                text += f"<b>{title}</b>\n"
                text += f"ID: {device_id}\n"
                if description:
                    text += f"Описание: {description}\n"
                text += f"Статус: {status}\n"
                text += f"Адрес: {device.get('address', 'Не указан')}\n"
                text += "─" * 20 + "\n"
                
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"{title} ({'🟢' if active else '🔴'})",
                        callback_data=f"device_{device_id}"
                    )
                ])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons + [
                [InlineKeyboardButton(text="➕ Добавить устройство", callback_data="add_device")],
                [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
            ])
            
            await message.answer(text, reply_markup=keyboard)
            
    except Exception as e:
        logger.error('Error listing devices', exc_info=True)
        await message.answer("❌ Произошла ошибка при получении списка устройств.")


async def add_device_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handle callback for adding device
    """
    await callback.answer()
    await add_device_start(callback.message, state)


async def add_device_start(message: Message, state: FSMContext):
    """
    Start adding device process
    """
    try:
        user_id = message.from_user.id
        
        async with APIClient() as client:
            user = await client.get_user_by_id(user_id)
            if not user or not user.get('active', True):
                await message.answer("❌ Ваш аккаунт заблокирован или вы не зарегистрированы.")
                return
        
        await state.set_state(DeviceStates.waiting_for_title)
        await message.answer(
            "➕ <b>Добавление нового устройства</b>\n\n"
            "Введите название устройства:"
        )
    except Exception as e:
        logger.error('Error starting add device', exc_info=True)
        await message.answer("❌ Произошла ошибка.")


async def process_title(message: Message, state: FSMContext):
    """
    Process device title
    """
    title = message.text.strip()
    if not title or len(title) > 100:
        await message.answer("❌ Название не может быть пустым или длиннее 100 символов. Попробуйте снова:")
        return
    
    await state.update_data(title=title)
    await state.set_state(DeviceStates.waiting_for_description)
    await message.answer("Введите описание устройства:")


async def process_description(message: Message, state: FSMContext):
    """
    Process device description
    """
    description = message.text.strip()
    if len(description) > 500:
        await message.answer("❌ Описание не может быть длиннее 500 символов. Попробуйте снова:")
        return
    
    await state.update_data(description=description)
    await state.set_state(DeviceStates.waiting_for_address)
    await message.answer("Введите адрес устройства (например, комната, IP-адрес и т.д.):")


async def process_address(message: Message, state: FSMContext):
    """
    Process device address and create device
    """
    address = message.text.strip()
    if not address or len(address) > 200:
        await message.answer("❌ Адрес не может быть пустым или длиннее 200 символов. Попробуйте снова:")
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
            f"✅ <b>Устройство успешно добавлено!</b>\n\n"
            f"Название: {device.get('title')}\n"
            f"ID: {device.get('device_id')}\n"
            f"Адрес: {device.get('address')}"
        )
        
    except Exception as e:
        logger.error('Error creating device', exc_info=True)
        await message.answer("❌ Произошла ошибка при создании устройства. Попробуйте позже.")
        await state.clear()


async def device_action_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handle callback for device actions
    """
    await callback.answer()
    
    try:
        device_id = int(callback.data.split('_')[1])
        user_id = callback.from_user.id
        
        async with APIClient() as client:
            device = await client.get_device_by_id(device_id)
            if not device:
                await callback.message.answer("❌ Устройство не найдено.")
                return
            
            # Check if device belongs to user
            user = await client.get_user_by_id(user_id)
            if not user or device_id not in user.get('devices', []):
                await callback.message.answer("❌ У вас нет доступа к этому устройству.")
                return
            
            active = device.get('active', False)
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🟢 Включить" if not active else "🔴 Выключить",
                        callback_data=f"toggle_{device_id}"
                    )
                ],
                [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{device_id}")],
                [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="list_devices")]
            ])
            
            await callback.message.answer(
                f"<b>{device.get('title')}</b>\n\n"
                f"ID: {device_id}\n"
                f"Описание: {device.get('description', 'Не указано')}\n"
                f"Адрес: {device.get('address', 'Не указан')}\n"
                f"Статус: {'🟢 Включено' if active else '🔴 Выключено'}\n"
                f"Создано: {device.get('create_time', 'Неизвестно')}",
                reply_markup=keyboard
            )
            
    except Exception as e:
        logger.error('Error in device action callback', exc_info=True)
        await callback.message.answer("❌ Произошла ошибка.")


async def toggle_device_callback(callback: CallbackQuery):
    """
    Handle toggle device callback
    """
    await callback.answer()
    
    try:
        device_id = int(callback.data.split('_')[1])
        user_id = callback.from_user.id
        
        async with APIClient() as client:
            device = await client.get_device_by_id(device_id)
            if not device:
                await callback.message.answer("❌ Устройство не найдено.")
                return
            
            user = await client.get_user_by_id(user_id)
            if not user or device_id not in user.get('devices', []):
                await callback.message.answer("❌ У вас нет доступа к этому устройству.")
                return
            
            # Toggle device
            new_active = not device.get('active', False)
            await client.update_device(device_id, {"active": new_active})
            
            status_text = "включено" if new_active else "выключено"
            await callback.message.answer(f"✅ Устройство {status_text}.")
            
            # Update the device list
            await list_devices_handler(callback.message)
            
    except Exception as e:
        logger.error('Error toggling device', exc_info=True)
        await callback.message.answer("❌ Произошла ошибка при изменении статуса устройства.")


async def delete_device_callback(callback: CallbackQuery):
    """
    Handle delete device callback
    """
    await callback.answer()
    
    try:
        device_id = int(callback.data.split('_')[1])
        user_id = callback.from_user.id
        
        async with APIClient() as client:
            device = await client.get_device_by_id(device_id)
            if not device:
                await callback.message.answer("❌ Устройство не найдено.")
                return
            
            user = await client.get_user_by_id(user_id)
            if not user or device_id not in user.get('devices', []):
                await callback.message.answer("❌ У вас нет доступа к этому устройству.")
                return
            
            await client.delete_device(device_id, user_id)
            await callback.message.answer(f"✅ Устройство '{device.get('title')}' удалено.")
            
            # Update the device list
            await list_devices_handler(callback.message)
            
    except Exception as e:
        logger.error('Error deleting device', exc_info=True)
        await callback.message.answer("❌ Произошла ошибка при удалении устройства.")


async def help_callback(callback: CallbackQuery):
    """
    Handle help callback
    """
    await callback.answer()
    await callback.message.answer(
        "📋 <b>Доступные команды:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать справку\n"
        "/devices - Показать все ваши устройства\n"
        "/add_device - Добавить новое устройство\n"
        "/menu - Показать главное меню\n\n"
        "💡 Используйте кнопки меню для быстрого доступа к функциям."
    )


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

