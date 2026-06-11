from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject
from aiogram.exceptions import TelegramBadRequest
from typing import Callable, Dict, Any, Awaitable
import contextlib

class AnswerCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
            else:
                raise
        finally:
            if isinstance(event, CallbackQuery):
                with contextlib.suppress(Exception):
                    await event.answer()
