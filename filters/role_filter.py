from aiogram.filters import BaseFilter
from aiogram.types import Message
from database.models import UserDb


class IsRoot(BaseFilter):
    async def __call__(self, message: Message, root_id: int) -> bool:
        return message.from_user.id == root_id


class IsRegistredUser(BaseFilter):
    async def __call__(self, message: Message, user_db: UserDb) -> bool:
        return message.from_user.id == user_db.user_id
