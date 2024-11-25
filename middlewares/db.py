from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, MessageReactionUpdated, TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.orm_query import orm_get_user, orm_update_user


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)


class FindUserInDB(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        message: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        match message:
            case Message():
                tg_user = message.from_user
            case MessageReactionUpdated():
                tg_user = message.user
            case _:
                return

        async with self.session_pool() as session:
            # username = message.from_user.username
            user = await orm_get_user(session, tg_user.username)

            if user is not None:
                user.user_id = tg_user.id
                await orm_update_user(session, tg_user.username, user)
                data["user_db"] = user
                data["session"] = session
            else:
                data["user_db"] = None
            return await handler(message, data)
