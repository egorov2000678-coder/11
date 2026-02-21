from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Account, Transaction


class TransactionsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, tx: Transaction) -> Transaction:
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def list_by_account(self, account_id: int, limit: int = 10) -> list[Transaction]:
        result = await self.session.scalars(
            select(Transaction)
            .where(or_(Transaction.from_account_id == account_id, Transaction.to_account_id == account_id))
            .order_by(Transaction.id.desc())
            .limit(limit)
        )
        return list(result)

    async def list_by_user(self, user_id: int, limit: int = 20) -> list[Transaction]:
        account_ids = select(Account.id).where(Account.user_id == user_id)
        result = await self.session.scalars(
            select(Transaction)
            .where(
                or_(
                    Transaction.from_account_id.in_(account_ids),
                    Transaction.to_account_id.in_(account_ids),
                )
            )
            .order_by(Transaction.id.desc())
            .limit(limit)
        )
        return list(result)
