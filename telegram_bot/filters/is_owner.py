from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from globals import get_bot_owner

class IsOwner(BaseFilter):
    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        owner = await get_bot_owner()
        return obj.from_user.id == owner
