import logging

from aiogram import types, Router, Bot

from bot.utils.copy_messages import notify_admins, send_file_to_super_admins

router = Router()


@router.error()
async def error_handler(event: types.ErrorEvent, bot: Bot):
    logging.critical("Critical error caused by %s", event.exception, exc_info=True)
    await notify_admins(
        bot,
        f"Critical error caused by <code>{event.exception}</code>"
    )
    await send_file_to_super_admins(bot, str(event))
