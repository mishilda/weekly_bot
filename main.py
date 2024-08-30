import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import other_handlers
from database.engine import Engine


logger = logging.getLogger(__name__)


async def on_startup(engine: Engine):
    run_param = False
    if run_param:
        await engine.drop_db

    await engine.create_db


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info("Starting bot")

    config: Config = load_config()

    engine = Engine(config.db)

    bot = Bot(
        token=config.tg_bot.token,
    )

    await on_startup(engine)

    dp = Dispatcher()
    dp.workflow_data.update({"rooot_id": config.tg_bot.root_id})

    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
