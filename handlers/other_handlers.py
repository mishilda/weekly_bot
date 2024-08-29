from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from filters import test_filter


router = Router()
router.message.filter(test_filter.MyTestFilter())


@router.message(Command(commands=["get_id"]))
async def process_get_id_command(message: Message):
    await message.answer(str(message.from_user.id))


@router.message(Command(commands=["get_chat_id"]))
async def process_get_chat_id_command(message: Message):
    await message.answer(str(message.chat.id))
