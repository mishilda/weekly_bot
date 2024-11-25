from __future__ import annotations

import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message, MessageReactionUpdated
from aiogram import Bot

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_get_user_by_topic,
    orm_get_message_by_private,
    orm_get_message_by_topic,
)
from database.models import UserDb


logger = logging.getLogger(__name__)


class IsTransferedMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == message.chat.id


class IsMainGroup(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        return message.chat.id == bot.my_main_chat


class IsGeneralTopic(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.message_thread_id is None or message.is_topic_message is False


class IsTransferTopic(BaseFilter):
    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        # return message.message_thread_id is not None and message.is_topic_message == True
        if message.message_thread_id is not None:
            to_user = await orm_get_user_by_topic(session, message.message_thread_id)
            if to_user is None:
                return False
            if to_user.user_id is None:
                logging.critical(f"empty user_id {to_user.username}")
                return False
            return {"to_user": to_user}
        return False


class IsExistsInTopic(BaseFilter):
    async def __call__(
        self, message: Message | MessageReactionUpdated, session: AsyncSession
    ) -> bool:
        edit_message = await orm_get_message_by_topic(session, message.message_id)
        if edit_message is None:
            return False
        return {"edited_message": edit_message}


class IsExistsInChat(BaseFilter):
    async def __call__(
        self, message: Message | MessageReactionUpdated, session: AsyncSession
    ) -> bool:
        match message:
            case Message():
                user = message.from_user
            case MessageReactionUpdated():
                user = message.user
            case _:
                return False

        edit_message = await orm_get_message_by_private(
            session, message.message_id, user.id
        )

        if edit_message is None:
            return False
        return {"edited_message": edit_message}
