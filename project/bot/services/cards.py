from __future__ import annotations

import random
from datetime import datetime

from bot.models import Account, Card, CardStatus, CardType
from bot.repositories import CardsRepository


class CardService:
    def __init__(self, cards_repo: CardsRepository) -> None:
        self.cards_repo = cards_repo

    async def issue_virtual(self, account: Account, holder_name: str) -> Card:
        card = Card(
            account_id=account.id,
            card_number="".join(str(random.randint(0, 9)) for _ in range(16)),
            holder_name=holder_name,
            expiry_month=f"{random.randint(1, 12):02d}",
            expiry_year=f"{(datetime.utcnow().year + 3) % 100:02d}",
            cvv=f"{random.randint(0, 999):03d}",
            card_type=CardType.VIRTUAL,
            status=CardStatus.ACTIVE,
        )
        return await self.cards_repo.save(card)

    async def set_status(self, card: Card, status: CardStatus) -> Card:
        card.status = status
        return await self.cards_repo.save(card)
