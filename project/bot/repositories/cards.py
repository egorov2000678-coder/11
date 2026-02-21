from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.models import Account, Card


class CardsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, card_id: int) -> Card | None:
        return await self.session.scalar(select(Card).options(selectinload(Card.account)).where(Card.id == card_id))

    async def list_by_user(self, user_id: int) -> list[Card]:
        result = await self.session.scalars(
            select(Card)
            .join(Account, Card.account_id == Account.id)
            .where(Account.user_id == user_id)
            .order_by(Card.id.desc())
        )
        return list(result)

    async def save(self, card: Card) -> Card:
        self.session.add(card)
        await self.session.flush()
        return card
