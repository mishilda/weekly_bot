import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import other_handlers, root_handlers, transfer_handlers, group_handlers
from database.engine import Engine

from middlewares.db import DataBaseSession, FindUserInDB


logger = logging.getLogger(__name__)


async def on_startup(engine: Engine):
    run_param = False
    if run_param:
        engine.drop_db()

    engine.create_db()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
        "[%(asctime)s] - %(name)s - %(message)s",
    )

    logger.info("Starting bot")

    config: Config = load_config()

    engine = Engine(config.db)

    bot = Bot(
        token=config.tg_bot.token,
    )

    bot.my_main_chat = config.tg_bot.root_chat_id

    # await on_startup(engine)

    await engine.create_db()

    dp = Dispatcher()
    dp.workflow_data.update(
        {"root_id": config.tg_bot.root_id, "root_chat": config.tg_bot.root_chat_id}
    )

    dp.include_router(root_handlers.rootRouter)
    root_handlers.rootRouter.message.middleware(
        DataBaseSession(engine.session_maker))

    dp.include_router(group_handlers.group_router)
    group_handlers.group_router.message.middleware(
        DataBaseSession(engine.session_maker)
    )

    dp.include_router(transfer_handlers.transfer_router)
    transfer_handlers.transfer_router.message.outer_middleware(
        FindUserInDB(engine.session_maker)
    )

    transfer_handlers.transfer_router.edited_message.outer_middleware(
        FindUserInDB(engine.session_maker)
    )

    transfer_handlers.transfer_router.message_reaction.outer_middleware(
        FindUserInDB(engine.session_maker)
    )

    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
