import asyncio
import base64
import io
import logging
import sys
from datetime import datetime
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile, BotCommand
from dotenv import load_dotenv

from middleware import LongTimeMiddleware
from utils import parse_html_to_md

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.message.middleware(LongTimeMiddleware())


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"🌟 <b>Привет, {message.from_user.full_name}!</b> 👋\n"
                         f"\n"
                         f"Рад тебя видеть! Я — Markdown Converter Bot, твой помощник в создании аккуратных Markdown-файлов из Telegram-сообщений. 📄✨\n"
                         f"\n"
                         f"Просто <b>перешли мне пост</b> с текстом, картинками 🖼️ или <code>кодом</code> — и я мгновенно превращу его в удобный файл с идеальным форматированием!\n"
                         f"\n"
                         f"🚀 <b>Попробуй прямо сейчас</b> — это займет всего пару секунд!\n"
                         f"\n"
                         f"<b>Как пользоваться?</b> Легко:\n"
                         f"1️⃣ Отправь мне любое сообщение из Telegram.\n"
                         f"2️⃣ Получи готовый Markdown-файл. 📂\n"
                         f"\n"
                         f"Готов упростить твою работу с текстами? Начинаем! 😊\n"
                         f"<i>Повторить описание более подробно можно в любой момент командой -</i> /help"
                         )


@dp.message(Command(commands=["help"]), flags={"long_operation": True})
async def command_help_handler(message: Message) -> None:
    help_message = await message.answer("<b>📄 Markdown Converter Bot</b>\n"
                                        "\n"
                                        "<i>Превращай Telegram-посты в красивые Markdown-файлы!</i>\n"
                                        "\n"
                                        "✨ <b>Что умеет этот бот?</b> ✨\n"
                                        "\n"
                                        "🔹 <b>Конвертирует</b> текст со стилями Telegram (<b>жирный</b>, <i>курсив</i>, <code>моноширинный</code> и др.) в Markdown-разметку.  \n"
                                        "🔹 <b>Сохраняет</b> форматирование: заголовки, списки, ссылки и даже <code>код</code>!\n"
                                        "🔹 <b>Добавляет картинки</b> 🖼️ – если в посте есть изображения, они встроятся в файл.\n"
                                        "🔹 <b>Отправляет готовый файл</b> 📂 – скачивай и используй в своих проектах!\n"
                                        "\n"
                                        "💡 <b>Как использовать?</b>\n"
                                        "Просто <b>перешли</b> боту любой пост или сообщение – и получи <u>Markdown-документ</u> в ответ!  \n"
                                        "\n"
                                        "🚀 <i>Идеально для:</i>"
                                        "• 📝 Конспектирования полезных постов  \n"
                                        "• 📚 Создания документации\n"
                                        "• 💾 Сохранения красивого форматирования  \n"
                                        "\n"
                                        "<b>Попробуй прямо сейчас!</b>"
                                        )
    parsed_message = parse_html_to_md(help_message.html_text, help_message.entities)
    cur_date = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    text_file = BufferedInputFile(parsed_message.encode(encoding="utf-8"), filename=f"{cur_date}.md")
    await message.answer_document(text_file, caption=f"👆Пример, предыдущее сообщение в Markdown")


@dp.message(F.text, flags={"long_operation": True})
async def parse_message(message: Message) -> None:
    try:
        if not message.entities:
            await message.answer(
                message.text if message.text else "Что-то не так!")
            return
        parsed_message = parse_html_to_md(message.html_text, message.entities)
        # parsed_message = parse_text_to_md(message.text, message.entities)
        cur_date = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        text_file = BufferedInputFile(parsed_message.encode(encoding="utf-8"), filename=f"{cur_date}.md")
        await message.answer_document(text_file)
    except TypeError:
        await message.answer("Что-то не так!")


@dp.message(F.caption & (F.media_group_id == None), flags={"long_operation": True})
async def parse_message_with_caption(message: Message) -> None:
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
    except TypeError:
        await message.answer("Что-то не так!")


@dp.message()
async def unknown_handler(message: Message) -> None:
    await message.answer("Такой тип сообщений не обрабатывается!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    commands = [
        BotCommand(command="/start", description="🏁 Старт"),
        BotCommand(command="/help", description="❓ Помощь"),
    ]
    await bot.set_my_commands(commands)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
