from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsRoot(BaseFilter):
    async def __call__(self, message: Message, root_id: int) -> bool:
        return message.from_user.id == root_id
