from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, and_f
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_get_user, orm_get_user_by_topic, orm_add_user
from filters.chat_type_filter import IsMainGroup, IsGeneralTopic, IsTransferTopic


group_router = Router()
group_router.message.filter(IsMainGroup())


@group_router.message(and_f(Command(commands="add"), IsGeneralTopic()))
async def process_add_command(
    message: Message, command: CommandObject, session: AsyncSession
):
    if command.args is None:
        await message.answer("No username in args")
        return

    username = command.args
    user = await orm_get_user(session, username)
    if user is None:
        user_dict = {
            "username": command.args,
            "role": "regular",
            "is_mute": False,
            "user_id": None,
        }

        await orm_add_user(session, user_dict)
        await message.answer("Ok")

    else:
        await message.answer(f"{username} already exists")


@group_router.message(IsTransferTopic())
async def process_text_to_command(
    message: Message, bot: Bot, session: AsyncSession
):
    user = await orm_get_user_by_topic(session, message.message_thread_id)

    if user is None:
        await message.answer(f"No such user in base: {message.message_thread_id}")
    elif user.user_id is None:
        await message.answer("user need to text to bot")
    else:
        await bot.copy_message(user.user_id, message.chat.id, message.message_id)