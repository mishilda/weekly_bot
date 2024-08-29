from aiogram.filters import BaseFilter
from aiogram.types import Message


class MyTestFilter(BaseFilter):
    async def __call__(self, message: Message, admin_id) -> bool:
        if message.from_user.id == admin_id:
            return True
        return False
