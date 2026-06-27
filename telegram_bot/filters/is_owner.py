from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from config import OWNER_ID

class IsOwner(BaseFilter):
    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        return obj.from_user.id == OWNER_ID
