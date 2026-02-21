from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.profile import profile_kb
from bot.models import Account, Transaction, User

router = Router()


@router.callback_query(F.data == "profile:show")
async def profile_show(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    accounts_count = await session.scalar(select(func.count(Account.id)).where(Account.user_id == user.id))
    tx_count = await session.scalar(
        select(func.count(Transaction.id)).where(
            (Transaction.from_account_id.in_(select(Account.id).where(Account.user_id == user.id)))
            | (Transaction.to_account_id.in_(select(Account.id).where(Account.user_id == user.id)))
        )
    )
    role = "Админ" if user.is_admin else "Пользователь"
    text = (
        f"👤 Профиль\nID: {user.id}\nTelegram ID: {user.telegram_id}\n"
        f"Username: @{user.username or '-'}\nРоль: {role}\n"
        f"Счетов: {accounts_count or 0}\nТранзакций: {tx_count or 0}"
    )
    await callback.message.edit_text(text, reply_markup=profile_kb())
    await callback.answer()
