from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Account


class AccountsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, account_id: int) -> Account | None:
        return await self.session.get(Account, account_id)

    async def get_by_number(self, account_number: str) -> Account | None:
        return await self.session.scalar(select(Account).where(Account.account_number == account_number))

    async def list_by_user(self, user_id: int) -> list[Account]:
        result = await self.session.scalars(select(Account).where(Account.user_id == user_id).order_by(Account.id.desc()))
        return list(result)

    async def save(self, account: Account) -> Account:
        self.session.add(account)
        await self.session.flush()
        return account
