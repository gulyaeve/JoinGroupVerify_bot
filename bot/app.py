import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiohttp import web

from bot.handlers import joining, error
from bot.settings import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Настройка сессии на кастомный api server
session = AiohttpSession(api=TelegramAPIServer.from_base(settings.api_server_url, is_local=True))

# Объект бота
bot = Bot(
    token=settings.TELEGRAM_API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=session,
)

# Storage
# redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
# storage = RedisStorage(redis_client)

# Объект диспетчера
# dp = Dispatcher(storage=storage)
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)


# Регистрация основных роутеров
dp.include_router(joining.router)

# Роутер для всех видов контента, которые не попали в предыдущие

# Роутер для обработки ошибок
dp.include_router(error.router)

# Роутеры для включения и выключения
# dp.include_router(startup.router)
# dp.include_router(shutdown.router)


async def webhook_register(bot: Bot):
    await bot.delete_webhook()
    await bot.set_webhook(url=settings.webhook, secret_token=settings.WEBHOOK_SECRET)


# Запуск бота
def launch_webhook():
    # await dp.start_polling(bot)
    dp.startup.register(webhook_register)

    # Create aiohttp.web.Application instance
    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host="0.0.0.0", port=settings.WEBHOOK_PORT, path=settings.WEBHOOK_PATH)


async def launch_polling():
    await bot.delete_webhook()
    await dp.start_polling(bot)
