import asyncio
import base64
import io
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile, BotCommand, FSInputFile
from aiogram.enums import ContentType
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_i18n.cores import FluentRuntimeCore
from aiogram_i18n import I18nContext, I18nMiddleware
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage
from redis.asyncio import client

from config import config
from middleware import (
    LongTimeMiddleware,
    MediaGroupMiddleware,
    LocaleManageMiddleware,
    DevModeMiddleware,
    LoggerMiddleware,
)
from utils import parse_html_to_md


redis = (
    client.Redis(password=config.REDIS_PASSWORD, host=config.REDIS_HOST)
    if config.APP_MODE == "prod"
    else None
)

dp = Dispatcher(
    storage=MemoryStorage() if config.APP_MODE == "dev" else RedisStorage(redis)
)

logger = logging.getLogger(__name__)


@dp.message(CommandStart())
async def command_start_handler(message: Message, i18n: I18nContext) -> None:
    """
    Start command handler. Answer Start message
    :param message: TG Message
    :param i18n: i18n Context
    :return:
    """
    await message.answer(i18n.get("start-message", user=message.from_user.full_name))


@dp.message(Command(commands=["example"]))
async def command_start_handler(message: Message, i18n: I18nContext) -> None:
    """
    Example command handle. Send example message and after transform to markdown file and send
    :param message: TG Message
    :param i18n: i18n Context
    :return:
    """
    media_group = MediaGroupBuilder(caption=i18n.get("example-message"))
    example_photo_1 = FSInputFile(Path(__file__).parent.resolve() / "img" / "tg.png")
    example_photo_2 = FSInputFile(Path(__file__).parent.resolve() / "img" / "md.png")
    media_group.add_photo(example_photo_1)
    media_group.add_photo(example_photo_2)
    example_message = await message.answer_media_group(media=media_group.build())

    await parse_message_with_media_group(example_message[0], example_message, i18n)


@dp.message(Command(commands=["help"]), flags={"long_operation": True})
async def command_help_handler(message: Message, i18n: I18nContext) -> None:
    """
    Help command handle. Send help message
    :param message: TG Message
    :param i18n: i18n Context
    :return:
    """
    await message.answer(i18n.get("help-message"))


@dp.message(Command(commands=["language_ru"]))
async def command_set_ru_lang(message: Message, i18n: I18nContext) -> None:
    """
    Changing language to Russian command handle. Changing user locale to Russian and sent notification about this.
    :param message: TG Message
    :param i18n: i18n Context
    :return:
    """
    try:
        await i18n.set_locale("ru")
        await message.answer(i18n.get("change-lang"))
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message(Command(commands=["language_en"]))
async def command_set_en_lang(message: Message, i18n: I18nContext) -> None:
    """
    Changing language to English command handle. Changing user locale to English and sent notification about this.
    :param message: TG Message
    :param i18n: i18n Context
    :return:
    """
    try:
        await i18n.set_locale("en")
        await message.answer(i18n.get("change-lang"))
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message(F.text, flags={"long_operation": True})
async def parse_message(message: Message, i18n: I18nContext) -> None:
    """
    Clear text handle. Transforming text from telegram markup to markdown markup and sent it's into markdown file.
    :param message: TG Message
    :param i18n: i18n Context
    :return:
    """
    try:
        parsed_message = parse_html_to_md(message.html_text, message.entities)
        cur_date = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        text_file = BufferedInputFile(
            parsed_message.encode(encoding="utf-8"), filename=f"{cur_date}.md"
        )
        await message.answer_document(text_file)
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message(F.caption & (F.media_group_id == None), flags={"long_operation": True})
async def parse_message_with_caption(message: Message, i18n: I18nContext) -> None:
    """
    Text with single media data handle. Transforming text from telegram markup to markdown markup,
    transform image to base64 encoding string-link and sent it's into markdown file.
    :param message: TG Message
    :param i18n: i18n Context
    :return:
    """
    try:
        parsed_message = parse_html_to_md(message.html_text, message.caption_entities)
        cur_date = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        if message.photo:
            buffer = io.BytesIO()
            await message.bot.download(message.photo[-1].file_id, destination=buffer)
            b64_stream_value = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()
            parsed_message += (
                f"\n\n![TG_PHOTO](data:image/jpeg;base64,{b64_stream_value})"
            )
        text_file = BufferedInputFile(
            parsed_message.encode(encoding="utf-8"), filename=f"{cur_date}.md"
        )
        await message.answer_document(text_file)
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message(
    (F.content_type == ContentType.PHOTO) & (F.media_group_id is not None),
    flags={"get_media_group": True, "long_operation": True},
)
async def parse_message_with_media_group(
    message: Message, album: List[Message] | None, i18n: I18nContext
) -> None:
    """
    Text with multiple media data handle. Transforming text from telegram markup to markdown markup,
    transform each image to base64 encoding string-link and sent it's into markdown file.
    :param message: TG Message
    :param album: Array of TG Message containing Photo
    :param i18n: i18n Context
    :return:
    """
    try:
        parsed_message = parse_html_to_md(message.html_text, message.caption_entities)
        cur_date = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        for message_photo in album:
            buffer = io.BytesIO()
            await message_photo.bot.download(
                message_photo.photo[-1].file_id, destination=buffer
            )
            b64_stream_value = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()
            parsed_message += (
                f"\n\n![TG_PHOTO](data:image/jpeg;base64,{b64_stream_value})"
            )
        text_file = BufferedInputFile(
            parsed_message.encode(encoding="utf-8"), filename=f"{cur_date}.md"
        )
        await message.answer_document(text_file)
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message()
async def unknown_handler(message: Message, i18n: I18nContext) -> None:
    """
    Handler for all other messages.
    :param message: TG Message
    :param i18n: i18n Context
    :return:
    """
    await message.answer(i18n.get("unsupported-message"))


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp.message.middleware(LoggerMiddleware())
    dp.message.middleware(DevModeMiddleware())
    dp.message.middleware(MediaGroupMiddleware())
    dp.message.middleware(LongTimeMiddleware())

    commands = [
        BotCommand(command="/start", description="🏁 Start"),
        BotCommand(command="/help", description="❓ Help"),
        BotCommand(command="/example", description="📲 Example"),
        BotCommand(command="/language_ru", description="🇷🇺 RU Language"),
        BotCommand(command="/language_en", description="🇬🇧 EN Language"),
    ]
    await bot.set_my_commands(commands)

    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(
            path="locales/{locale}/LC_MESSAGES",
        ),
        default_locale="en",
        manager=LocaleManageMiddleware(),
    )
    i18n_middleware.setup(dispatcher=dp)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=config.LOG_LEVEL, format=config.LOV_FORMAT, stream=sys.stdout
    )
    asyncio.run(main())
