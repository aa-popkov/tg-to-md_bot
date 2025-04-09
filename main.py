import asyncio
import base64
import io
import logging
import sys
from datetime import datetime
from os import getenv
from typing import List

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile, BotCommand
from aiogram.enums import ContentType
from aiogram_i18n.cores import FluentRuntimeCore
from dotenv import load_dotenv
from aiogram_i18n import I18nContext, LazyProxy, I18nMiddleware

from middleware import LongTimeMiddleware, MediaGroupMiddleware, LocaleManageMiddleware
from utils import parse_html_to_md

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.message.middleware(MediaGroupMiddleware())
dp.message.middleware(LongTimeMiddleware())

logger = logging.getLogger(__name__)


@dp.message(CommandStart())
async def command_start_handler(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("start-message", user=message.from_user.full_name))


@dp.message(Command(commands=["help"]), flags={"long_operation": True})
async def command_help_handler(message: Message, i18n: I18nContext) -> None:
    help_message = await message.answer(i18n.get("help-message"))
    parsed_message = parse_html_to_md(help_message.html_text, help_message.entities)
    cur_date = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    text_file = BufferedInputFile(parsed_message.encode(encoding="utf-8"), filename=f"{cur_date}.md")
    await message.answer_document(text_file, caption=i18n.get("help-message-example"))


@dp.message(Command(commands=["language_ru"]))
async def command_set_ru_lang(message: Message, i18n: I18nContext) -> None:
    try:
        await i18n.set_locale("ru")
        await message.answer(i18n.get("change-lang"))
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message(Command(commands=["language_en"]))
async def command_set_en_lang(message: Message, i18n: I18nContext) -> None:
    try:
        await i18n.set_locale("en")
        await message.answer(i18n.get("change-lang"))
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message(F.text, flags={"long_operation": True})
async def test_i18n(message: Message, i18n: I18nContext) -> None:
    try:
        name = message.from_user.mention_html()
        msg = i18n.get("hello", user=name)
        await message.reply(msg)
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message(F.text, flags={"long_operation": True})
async def parse_message(message: Message, i18n: I18nContext) -> None:
    try:
        if not message.entities:
            await message.answer(message.text)
            return
        parsed_message = parse_html_to_md(message.html_text, message.entities)
        cur_date = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        text_file = BufferedInputFile(parsed_message.encode(encoding="utf-8"), filename=f"{cur_date}.md")
        await message.answer_document(text_file)
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message(F.caption & (F.media_group_id == None), flags={"long_operation": True})
async def parse_message_with_caption(message: Message, i18n: I18nContext) -> None:
    try:
        parsed_message = parse_html_to_md(message.html_text, message.caption_entities)
        cur_date = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        if message.photo:
            buffer = io.BytesIO()
            await message.bot.download(message.photo[-1].file_id, destination=buffer)
            b64_stream_value = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()
            parsed_message += f"\n\n![TG_PHOTO](data:image/jpeg;base64,{b64_stream_value})"
        text_file = BufferedInputFile(parsed_message.encode(encoding="utf-8"), filename=f"{cur_date}.md")
        await message.answer_document(text_file)
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message((F.content_type == ContentType.PHOTO) & (F.media_group_id is not None),
            flags={"get_media_group": True, "long_operation": True}, )
async def parse_message_with_media_group(message: Message, album: List[Message] | None, i18n: I18nContext) -> None:
    try:
        parsed_message = parse_html_to_md(message.html_text, message.caption_entities)
        cur_date = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        for message_photo in album:
            buffer = io.BytesIO()
            await message_photo.bot.download(message_photo.photo[-1].file_id, destination=buffer)
            b64_stream_value = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()
            parsed_message += f"\n\n![TG_PHOTO](data:image/jpeg;base64,{b64_stream_value})"
        text_file = BufferedInputFile(parsed_message.encode(encoding="utf-8"), filename=f"{cur_date}.md")
        await message.answer_document(text_file)
    except Exception as ex:
        logger.error(ex)
        await message.answer(i18n.get("some-problem"))


@dp.message()
async def unknown_handler(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("unsupported-message"))


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    commands = [
        BotCommand(command="/start", description="🏁 Start"),
        BotCommand(command="/help", description="❓ Help"),
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
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
                        stream=sys.stdout)
    asyncio.run(main())
