from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram import Bot


class IsTransferedMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == message.chat.id


class IsMainGroup(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        return message.chat.id == bot.my_main_chat


class IsGeneralTopic(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.is_topic_message is True


class IsTransferTopic(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.message_thread_id is not None and message.is_topic_message == True
