from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, and_f
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_type_filter import IsTransferedMessage
from filters.role_filter import IsRegistredUser
from database.models import UserDb
from database.orm_query import orm_update_user


regularRouter = Router()
regularRouter.message.filter(and_f(IsTransferedMessage(), IsRegistredUser()))


# @regularRouter.message(Command(commands=["get_id"]))
# async def process_get_id_command(message: Message):
#     await message.answer(str(message.from_user.id))


# @regularRouter.message(Command(commands=["get_chat_id"]))
# async def process_get_chat_id_command(message: Message):
#     await message.answer(str(message.chat.id))


@regularRouter.message()
async def process_message(
    message: Message,
    bot: Bot,
    user_db: UserDb,
    session: AsyncSession
):
    if not user_db.chat_id:
        if user_db.name:
            name = user_db.name
        elif message.from_user.first_name:
            name = message.from_user.first_name
        elif message.from_user.last_name:
            name = message.from_user.last_name
        elif message.from_user.username:
            name = message.from_user.username
        else:
            name = message.from_user.id

        topic = await bot.create_forum_topic(bot.my_main_chat, name=name)
        user_db.chat_id = topic.message_thread_id
        await orm_update_user(session, user_db.username, user_db)

    try:
        # await bot.send_message(
        #     bot.my_main_chat,
        #     f"{message.from_user.username}: {message.text}",
        #     message_thread_id=user_db.chat_id
        # )
        await bot.copy_message(bot.my_main_chat, message.chat.id,
                               message.message_id, message_thread_id=user_db.chat_id)
# #
        # await message.send_copy(chat_id=bot.my_main_chat, reply_to_message_id=message.message_id)
    except TypeError:
        await message.reply(text="Can't sent this message.")
