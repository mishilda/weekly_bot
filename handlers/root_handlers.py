from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from filters.role_filter import IsRoot

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_get_user,
    orm_add_user
)


rootRouter = Router()
rootRouter.message.filter(IsRoot())


@rootRouter.message(Command(commands="init"))
async def process_set_group_command(
    message: Message, bot: Bot, session: AsyncSession
):
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("Только в чате группы")
    else:
        bot.my_main_chat = message.chat.id
        await message.answer("Ok")
        # user = message.from_user
        # user_db = await orm_get_user(session, user.id)
        # if user_db is None:
        #     user_dict = {
        #         "username": user.username,
        #         "role": "admin",
        #         "is_mute": False,
        #         "user_id": user.id
        #     }
        #     await orm_add_user(session, user_dict)
