from __future__ import annotations

from datetime import datetime, timezone

from bot.models import User
from bot.repositories import UsersRepository


class UserService:
    def __init__(self, users_repo: UsersRepository, admin_ids: set[int]) -> None:
        self.users_repo = users_repo
        self.admin_ids = admin_ids

    async def get_or_create_user(self, telegram_id: int, username: str | None) -> User:
        user = await self.users_repo.get_by_telegram_id(telegram_id)
        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                is_admin=telegram_id in self.admin_ids,
                is_banned=False,
            )
        else:
            user.username = username
            if telegram_id in self.admin_ids:
                user.is_admin = True
        user.last_activity_at = datetime.now(timezone.utc)
        return await self.users_repo.save(user)

    def ensure_not_banned(self, user: User) -> None:
        if user.is_banned:
            raise PermissionError("Ваш аккаунт заблокирован. Обратитесь в поддержку.")
