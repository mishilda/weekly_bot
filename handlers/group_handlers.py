from aiogram import Router, Bot
from aiogram.types import Message, MessageReactionUpdated
from aiogram.filters import Command, CommandObject, and_f
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_get_user,
    orm_get_user_by_topic,
    orm_add_user,
    orm_update_user,
    orm_delete_user
    )
from filters.chat_type_filter import IsMainGroup, IsGeneralTopic, IsTransferTopic


group_router = Router()
group_router.message.filter(and_f(IsMainGroup(), IsGeneralTopic()))


@group_router.message(Command(commands="add"))
async def process_add_command(
    message: Message, command: CommandObject, session: AsyncSession
):
    if command.args is None:
        await message.answer("No args")
        return

    try:
        username, name = [s.strip() for s in command.args.split(" ", maxsplit=1)]
        if name == "":
            await message.reply("Wrong format")
            return
    except ValueError:
        await message.reply("Wrong format")
        return

    user = await orm_get_user(session, username)
    if user is None:
        user_dict = {
            "username": username,
            "name": name,
            "role": "regular",
            "is_mute": False,
            "user_id": None,
        }

        await orm_add_user(session, user_dict)
        await message.answer("Ok")

    else:
        await message.answer(f"{username} already exists")


# @group_router.edited_message(IsTransferTopic())
# async def process_edit_message(message: Message):
#     await message.answer("Вижу редактированное сообщение!")


@group_router.message(Command(commands="edit_name"))
async def process_edit_command(
    message: Message, command: CommandObject, bot: Bot, session: AsyncSession
):
    if command.args is None:
        await message.reply("No args")
        return

    try:
        username, name = [s.strip() for s in command.args.split(" ", maxsplit=1)]
        if name == "":
            await message.reply("Wrong format")
            return
    except ValueError:
        await message.reply("Wrong format")
        return

    user = await orm_get_user(session, username)
    if user is None:
        await message.answer(f"{username} doesn't exist")
        return
    elif user.name == name:
        await message.answer("The same name")
        return
    else:
        user.name = name
        await orm_update_user(session, username, user)
        if user.chat_id is not None:
            await bot.edit_forum_topic(message.chat.id, user.chat_id, user.name)
        await message.answer("Ok")


@group_router.message(Command(commands="delete"))
async def process_delete_command(
    message: Message, command: CommandObject, bot: Bot, session: AsyncSession
):
    if command.args is None:
        await message.reply("No args")
        return

    username = command.args
    user = await orm_get_user(session, username)
    if user is None:
        await message.reply("f{username} doesn't exist")
        return
    if user.chat_id is not None:
        await bot.delete_forum_topic(message.chat.id, user.chat_id)
    await orm_delete_user(session, username)
    await message.reply("Ok")
