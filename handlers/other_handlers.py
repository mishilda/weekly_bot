from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from filters.chat_type_filter import IsMainGroup


router = Router()
router.message.filter(~IsMainGroup())


@router.message()
async def answer(message: Message):
    await message.answer("not in base")
