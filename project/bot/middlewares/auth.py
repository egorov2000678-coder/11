from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.repositories import UsersRepository
from bot.services import UserService
from config import Settings


class AuthMiddleware(BaseMiddleware):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session = data["session"]
        from_user = None
        if isinstance(event, Message):
            from_user = event.from_user
        elif isinstance(event, CallbackQuery):
            from_user = event.from_user
        if from_user is None:
            return await handler(event, data)

        users_repo = UsersRepository(session)
        user_service = UserService(users_repo, self.settings.admins)
        user = await user_service.get_or_create_user(from_user.id, from_user.username)
        user_service.ensure_not_banned(user)
        data["user"] = user
        return await handler(event, data)
