import asyncio
import logging
from typing import List, Union, Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject
from aiogram_i18n.managers import BaseManager
from aiogram.types.user import User

logger = logging.getLogger(__name__)


class LongTimeMiddleware(BaseMiddleware):
    clock_icons: List[str] = [
        "🕐",
        "🕑",
        "🕒",
        "🕓",
        "🕔",
        "🕕",
        "🕖",
        "🕗",
        "🕘",
        "🕙",
        "🕚",
        "🕛",
    ]
    msg = None

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        flag = get_flag(data, "long_operation")
        if not flag:
            return await handler(event, data)

        updated_task = asyncio.create_task(self.show_icon(event))
        try:
            await handler(event, data)
        finally:
            await self.hide_icon()
            updated_task.cancel()

    async def show_icon(self, event: Message):
        index = 0
        self.msg = await event.bot.send_message(event.chat.id, self.clock_icons[index])
        while True:
            await asyncio.sleep(0.5)
            index = index + 1 if index < len(self.clock_icons) - 1 else 0
            icon = self.clock_icons[index]
            await event.bot.edit_message_text(
                icon, str(self.msg.chat.id), self.msg.message_id
            )

    async def hide_icon(self):
        try:
            await self.msg.bot.delete_message(self.msg.chat.id, self.msg.message_id)
        except Exception as ex:
            logger.error("Cannot delete timer message!", self.msg.chat.id, ex)


class MediaGroupMiddleware(BaseMiddleware):
    album_data: dict[str, List[Message]] = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)
        flag = get_flag(data, "get_media_group")
        if not flag:
            return await handler(event, data)

        if self.album_data.get(event.media_group_id):
            self.album_data[event.media_group_id].append(event)
            return
        else:
            self.album_data[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)
            data["is_last"] = True
            data["album"] = self.album_data[event.media_group_id]

        try:
            await handler(event, data)
        finally:
            if event.media_group_id and data.get("is_last"):
                del self.album_data[event.media_group_id]


class LocaleManageMiddleware(BaseManager):
    async def get_locale(self, event_from_user: User, state: FSMContext) -> str:
        default = event_from_user.language_code or self.default_locale
        locale = await state.get_value("locale")
        if locale:
            return locale
        return default

    async def set_locale(
        self, locale: str, event_from_user: User, state: FSMContext
    ) -> None:
        await state.update_data({"locale": locale})
