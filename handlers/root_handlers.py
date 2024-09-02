from from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from filters.role_filter import IsRoot


rootRouter = Router()
rootRouter.message.filter(IsRoot())


@rootRouter.message(Command(commands='set_group'))
async def process_set_group_command(message: Message)