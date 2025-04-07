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
from utils import parse_text_to_md, parse_html_to_md

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.message.middleware(LongTimeMiddleware())


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command(commands=["help"]), flags={"long_operation": True})
async def command_help_handler(message: Message) -> None:
    help_message = await message.answer("""
<b>📄 Markdown Converter Bot</b>

<i>Превращай Telegram-посты в красивые Markdown-файлы!</i>

✨ <b>Что умеет этот бот?</b> ✨

🔹 <b>Конвертирует</b> текст со стилями Telegram (<b>жирный</b>, <i>курсив</i>, <code>моноширинный</code> и др.) в Markdown-разметку.  
🔹 <b>Сохраняет</b> форматирование: заголовки, списки, ссылки и даже <code>код</code>!
🔹 <b>Добавляет картинки</b> 🖼️ – если в посте есть изображения, они встроятся в файл.
🔹 <b>Отправляет готовый файл</b> 📂 – скачивай и используй в своих проектах!

💡 <b>Как использовать?</b>
Просто <b>перешли</b> боту любой пост или сообщение – и получи <u>Markdown-документ</u> в ответ!  

🚀 <i>Идеально для:</i>
• 📝 Конспектирования полезных постов  
• 📚 Создания документации
• 💾 Сохранения красивого форматирования  

<b>Попробуй прямо сейчас!</b>
    """)
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
        if not message.caption_entities:
            await message.answer(
                message.caption if message.caption else "Что-то не так!")
            return
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
