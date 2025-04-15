import logging
from enum import Enum
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppMode(str, Enum):
    DEV = "dev"
    PROD = "prod"


class Config(BaseSettings):
    APP_MODE: AppMode = AppMode.DEV

    BOT_TOKEN: str
    BOT_ADMIN_CHAT_ID: List[str] | None

    REDIS_HOST: str = "tg-to-md-bot-redis"
    REDIS_PASSWORD: str | None

    LOG_LEVEL: int | str = logging.INFO
    LOV_FORMAT: str = (
        "%(asctime)s - %(name)s - %(levelname)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Config()
