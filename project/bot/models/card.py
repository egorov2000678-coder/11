from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin
from bot.models.enums import CardStatus, CardType


class Card(Base, TimestampMixin):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    card_number: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    holder_name: Mapped[str] = mapped_column(String(64))
    status: Mapped[CardStatus] = mapped_column(Enum(CardStatus), default=CardStatus.ACTIVE)
    expiry_month: Mapped[str] = mapped_column(String(2))
    expiry_year: Mapped[str] = mapped_column(String(2))
    cvv: Mapped[str] = mapped_column(String(3))
    card_type: Mapped[CardType] = mapped_column(Enum(CardType), default=CardType.VIRTUAL)

    account = relationship("Account", back_populates="cards")
