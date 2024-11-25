from aiogram import Router, Bot
from aiogram.types import Message, ReplyParameters, MessageReactionUpdated
from aiogram.filters import and_f, or_f
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from filters.role_filter import IsRegistredUser
from filters.chat_type_filter import IsTransferedMessage, IsTransferTopic, IsExistsInTopic, IsExistsInChat

from database.models import UserDb, MessageDb
from database.orm_query import (
    orm_update_user,
    orm_add_message,
    orm_get_message_by_private,
    orm_get_message_by_topic,
)


transfer_router = Router()
transfer_router.message.filter(IsRegistredUser())


async def send_copy(
    bot: Bot,
    message: Message,
    dst_chat_id: int,
    message_thread_id: int,
    session: AsyncSession,
):

    try:
        reply_parameters = None
        if message.reply_to_message:
            replied_message = await orm_get_message_by_private(
                session, message.reply_to_message.message_id, message.chat.id
            )

            if replied_message is not None:
                reply_parameters = ReplyParameters(
                    message_id=replied_message.topic_id,
                    # chat_id=bot.my_main_chat
                )

        mess = await bot.copy_message(
            dst_chat_id,
            message.chat.id,
            message.message_id,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
        )
        data = {
            "private_id": message.message_id,
            "private_chat": message.chat.id,
            "topic_id": mess.message_id,
            "topic_chat": message_thread_id,
        }
        await orm_add_message(session, data)
    except TypeError:
        await message.reply(text="Can't sent this message.")
    # except TelegramBadRequest:
    #     raise ValueError


async def create_topic(bot: Bot, user_db: UserDb, session: AsyncSession):
    topic = await bot.create_forum_topic(bot.my_main_chat, name=user_db.name)
    user_db.chat_id = topic.message_thread_id
    await orm_update_user(session, user_db.username, user_db)


@transfer_router.message(IsTransferedMessage())
async def transfer_message_to_topic(
    message: Message, bot: Bot, user_db: UserDb, session: AsyncSession
):
    if not user_db.chat_id:
        await create_topic(bot, user_db, session)
    try:
        await send_copy(bot, message, bot.my_main_chat, user_db.chat_id, session)

    except TelegramBadRequest:
        await create_topic(bot, user_db, session)
        await send_copy(bot, message, bot.my_main_chat, user_db.chat_id, session)


@transfer_router.message(IsTransferTopic())
async def transfer_message_to_chat(
    message: Message, bot: Bot, user_db: UserDb, to_user: UserDb, session: AsyncSession
):
    try:
        reply_parameters = None
        if (
            message.reply_to_message is not None
            and message.reply_to_message.message_id != to_user.chat_id
        ):

            replied_message = await orm_get_message_by_topic(
                session, message.reply_to_message.message_id
            )
            if replied_message is not None:
                reply_parameters = ReplyParameters(
                    message_id=replied_message.private_id,
                    chat_id=to_user.user_id
                )

        from_message = await bot.send_message(to_user.user_id, f"{user_db.name} says:")
        mess = await bot.copy_message(
            to_user.user_id,
            message.chat.id,
            message.message_id,
            reply_parameters=reply_parameters,
        )
        data = {
            "private_id": mess.message_id,
            "private_chat": to_user.user_id,
            "topic_id": message.message_id,
            "topic_chat": message.message_thread_id,
        }
        await orm_add_message(session, data)
    except TypeError:
        await message.reply(text="Can't sent this message.")
        await bot.delete_message(to_user.user_id, from_message.message_id)


@transfer_router.edited_message(IsTransferTopic())
async def edit_in_chat(message: Message, bot: Bot, to_user: UserDb, session: AsyncSession):

    edited_message = await orm_get_message_by_topic(
        session, message.message_id
    )
    try:
        await bot.edit_message_text(
            message.text,
            chat_id=to_user.user_id,
            message_id=edited_message.private_id
        )
    except TelegramBadRequest:
        ...


@transfer_router.edited_message(IsTransferedMessage())
async def edit_in_topic(message: Message, bot: Bot,  session: AsyncSession):

    edited_message = await orm_get_message_by_private(
        session, message.message_id, message.from_user.id
    )
    try:
        await bot.edit_message_text(
            message.text,
            chat_id=bot.my_main_chat,
            message_id=edited_message.topic_id
        )
    except TelegramBadRequest:
        ...


@transfer_router.message_reaction(IsExistsInTopic())
async def transfer_react_to_chat(
    message_reaction: MessageReactionUpdated,
    edited_message: MessageDb,
    bot: Bot,
    session: AsyncSession
):
    try:

        await bot.set_message_reaction(
            edited_message.private_chat,
            edited_message.private_id,
            reaction=message_reaction.new_reaction
        )
    except TelegramBadRequest as e:
        print(e)


@transfer_router.message_reaction(IsExistsInChat())
async def transfer_react_to_topic(
    message_reaction: MessageReactionUpdated,
    edited_message: MessageDb,
    bot: Bot,
    session: AsyncSession
):
    try:
        await bot.set_message_reaction(
            bot.my_main_chat,
            edited_message.topic_id,
            reaction=message_reaction.new_reaction
        )
    except TelegramBadRequest as e:
        print(e)
