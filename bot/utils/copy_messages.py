import logging

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest

from bot.settings import settings
from bot.utils.utilities import make_bytes


async def notify_admins(bot: Bot, text: str, reply_markup=None):
    for bot_admin in settings.BOT_ADMINS:
        try:
            await bot.send_message(bot_admin, text, reply_markup=reply_markup)
        except TelegramBadRequest:
            logging.warning(f"Failed to send to [{bot_admin}]")


async def send_file_to_super_admins(bot: Bot, data: str, reply_markup=None):
    name = "error_info.txt"
    file: bytes = make_bytes(data, name)
    for bot_admin in settings.BOT_ADMINS:
        await bot.send_document(
            bot_admin,
            types.BufferedInputFile(file, name),
            reply_markup=reply_markup,
        )
