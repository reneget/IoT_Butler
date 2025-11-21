import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from configurations import main_config
from handlers import register_handlers
from log.config import logger


async def main():
    """
    Main function to start the bot
    """
    logger.info("Starting Telegram bot")
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=main_config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Register handlers
    register_handlers(dp)
    logger.info("Handlers registered")
    
    # Start polling
    logger.info("Bot started, waiting for messages...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

