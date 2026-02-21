from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User
from bot.repositories import TransactionsRepository

router = Router()


@router.message(Command("admin_transactions_by_user"))
async def admin_transactions_by_user(message: Message, user: User, session: AsyncSession) -> None:
    if not user.is_admin:
        await message.answer("Нет прав")
        return
    user_id = int(message.text.split()[1])
    txs = await TransactionsRepository(session).list_by_user(user_id, limit=20)
    if not txs:
        await message.answer("Операций нет")
        return
    lines = [f"{tx.created_at:%Y-%m-%d %H:%M} | {tx.type} | {tx.amount} {tx.currency}" for tx in txs]
    await message.answer("\n".join(lines))
