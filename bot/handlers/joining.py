import asyncio
import random

from aiogram import Bot, F, Router, types
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.fsm.state import State
from aiogram.types import ChatMemberUpdated, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
import logging

from bot.utils.copy_messages import notify_admins

ver = []
router = Router()

# Функция которая будет кикать через 60 секунд
async def kick(memberId: int, bot: Bot, channelId: int, mesId: int, user: str):
    await asyncio.sleep(20)
    if memberId not in ver:
        await notify_admins(text=f"{user} был заблокирован.", bot=bot)
        await bot.delete_message(channelId, mesId)
        await bot.ban_chat_member(channelId, memberId)
        try:
            await bot.unban_chat_member(channelId, memberId, only_if_banned=True)
        except TelegramBadRequest as e:
            logging.warning(e)
    else:
        ver.remove(memberId)

# Создание клавиатуры для верификации
def ver_ikb(correct: int, memberId: int) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    wrong = random.randint(0, 20)
    if wrong == correct:
        wrong += 5
    if wrong > correct:
        ikb.button(text=f"{correct}", callback_data=str(memberId))
        ikb.button(text=f'{wrong}', callback_data='No')
    else:
        ikb.button(text=f'{wrong}', callback_data='No')
        ikb.button(text=f"{correct}", callback_data=str(memberId))
    ikb.adjust(2)
    return ikb.as_markup()

# Функции хендлеров
async def new_member(event: ChatMemberUpdated, bot: Bot):
    f = random.randint(0, 10)
    s = random.randint(0, 10)
    print(event.new_chat_member)
    m = await bot.send_message(chat_id=event.chat.id,
            text=f"Добро пожаловать <b>@{event.new_chat_member.user.username}</b>!\nПройди верификацию за 20 секунд: \n{f} + {s} = ",
            reply_markup=ver_ikb(f + s, event.new_chat_member.user.id),
        )
    await kick(event.new_chat_member.user.id, bot, event.chat.id, m.message_id, event.new_chat_member.user.full_name)


# @router.callback_query(lambda callback: callback.data == str(callback.from_user.id))
async def not_kick(callback: types.CallbackQuery):
    ver.append(callback.from_user.id)
    await callback.answer('Вы успешно верифицировались!', show_alert=True)
    await callback.message.delete()

async def wrong_ans(callback: types.CallbackQuery):
    await callback.answer('Попробуй еще раз...')

async def wrong_user(callback: types.CallbackQuery):
    await callback.answer('Ты уже здесь свой, успокойся!')

# Регистрация хендлеров в роутер

router = Router()

router.chat_member.register(new_member, ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
router.callback_query.register(not_kick, lambda callback: callback.data == str(callback.from_user.id))
router.callback_query.register(wrong_ans, F.data == 'No')
router.callback_query.register(wrong_user, State())
