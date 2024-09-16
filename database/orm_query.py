from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserDb, MessageDb


async def orm_add_user(session: AsyncSession, data: dict):
    obj = UserDb(
        username=data["username"],
        role=data["role"],
        name=data["name"],
        is_mute=data["is_mute"],
        user_id=data["user_id"],
    )
    session.add(obj)
    await session.commit()


async def orm_get_user(session: AsyncSession, username: str):
    query = select(UserDb).where(UserDb.username == username)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_user_by_topic(session: AsyncSession, topic_id: int) -> UserDb:
    query = select(UserDb).where(UserDb.chat_id == topic_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_user(session: AsyncSession, username: str, data: UserDb):
    query = (
        update(UserDb)
        .where(UserDb.username == username)
        .values(
            username=data.username,
            role=data.role,
            is_mute=data.is_mute,
            user_id=data.user_id,
            chat_id=data.chat_id,
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_user(session: AsyncSession, username: str):
    query = delete(UserDb).where(UserDb.username == username)
    await session.execute(query)
    await session.commit()


async def orm_add_message(session: AsyncSession, data: dict):
    obj = MessageDb(
        private_id=data["private_id"],
        private_chat=data["private_chat"],
        topic_id=data["topic_id"],
        topic_chat=data["topic_chat"],
    )

    session.add(obj)
    await session.commit()


async def orm_get_message_by_private(
    session: AsyncSession, private_id: int, private_chat: int
):
    query = select(MessageDb).where(
        MessageDb.private_chat == private_chat, MessageDb.private_id == private_id
    )
    result = await session.execute(query)
    return result.scalar()


async def orm_get_message_by_topic(
    session: AsyncSession, topic_id: int, topic_chat: int
):
    query = select(MessageDb).where(
        MessageDb.topic_chat == topic_chat, MessageDb.topic_id == topic_id
    )
    result = await session.execute(query)
    return result.scalar()
