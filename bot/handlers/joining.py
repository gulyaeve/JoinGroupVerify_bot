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
time_to_join = 20


async def ban_user(
        member_id: int,
        bot: Bot,
        group_id: int,
        user_fullname: str
):
    await notify_admins(text=f"{user_fullname} был заблокирован.", bot=bot)
    await bot.ban_chat_member(group_id, member_id)
    await asyncio.sleep(1)
    try:
        await bot.unban_chat_member(group_id, member_id, only_if_banned=True)
    except TelegramBadRequest as e:
        logging.warning(e)
        await notify_admins(text=f"{user_fullname} скорее всего остался в черном списке группы. {e}", bot=bot)


# Функция которая будет кикать 
async def kick(
        member_id: int,
        bot: Bot,
        group_id: int,
        user_fullname: str
):
    await asyncio.sleep(time_to_join)
    user_in_group = await bot.get_chat_member(group_id, member_id)
    if member_id not in ver and user_in_group.status != 'left':
        await ban_user(
            member_id=member_id,
            bot=bot,
            group_id=group_id,
            user_fullname=user_fullname,
        )
    elif user_in_group.status != 'left':
        await notify_admins(text=f"{user_fullname} ответил правильно и прошел верификацию.", bot=bot)
        ver.remove(member_id)
    else:
        await notify_admins(text=f"{user_fullname} ответил неправильно.", bot=bot)


# Создание клавиатуры для верификации
def ver_ikb(correct: int, member_id: int) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    wrong = random.randint(0, 20)
    if wrong == correct:
        wrong += 5
    if wrong > correct:
        ikb.button(text=f"{correct}", callback_data=str(member_id))
        ikb.button(text=f'{wrong}', callback_data='No')
    else:
        ikb.button(text=f'{wrong}', callback_data='No')
        ikb.button(text=f"{correct}", callback_data=str(member_id))
    ikb.adjust(2)
    return ikb.as_markup()


# Функции хендлеров
async def new_member(event: ChatMemberUpdated, bot: Bot):
    f = random.randint(0, 10)
    s = random.randint(0, 10)
    await notify_admins(text=f"{event.new_chat_member}\nначал верификацию в группе {event.chat.full_name}.", bot=bot)
    await bot.send_message(chat_id=event.chat.id,
            text=f"Добро пожаловать <b>@{event.new_chat_member.user.full_name}</b>!\nПройди верификацию за {time_to_join} секунд: \n{f} + {s} = ",
            reply_markup=ver_ikb(f + s, event.new_chat_member.user.id),
        )
    await kick(
        member_id=event.new_chat_member.user.id,
        bot=bot,
        group_id=event.chat.id,
        user_fullname=event.new_chat_member.user.full_name,
    )


# @router.callback_query(lambda callback: callback.data == str(callback.from_user.id))
async def not_kick(callback: types.CallbackQuery):
    ver.append(callback.from_user.id)
    await callback.answer('Вы успешно верифицировались!', show_alert=True)
    await callback.message.delete()


async def wrong_ans(callback: types.CallbackQuery, bot: Bot):
    await ban_user(
        member_id=callback.from_user.id,
        bot=bot,
        group_id=callback.message.chat.id,
        user_fullname=callback.from_user.full_name,
    )
    await callback.message.delete()


async def wrong_user(callback: types.CallbackQuery):
    await callback.answer('Не твоё сообщение!')

# Регистрация хендлеров в роутер

router = Router()

router.chat_member.register(new_member, ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
router.callback_query.register(not_kick, lambda callback: callback.data == str(callback.from_user.id))
router.callback_query.register(wrong_ans, F.data == 'No')
router.callback_query.register(wrong_user, State())
