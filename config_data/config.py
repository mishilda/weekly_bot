from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    url: str


@dataclass
class TgBot:
    token: str
    root_id: int
    root_chat_id: int


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env("BOT_TOKEN"),
            root_id=env.int("ROOT_ID"),
            root_chat_id=env.int("ROOT_ID"),
        ),
        db=DatabaseConfig(url=env("DB_LITE")),
    )
