from __future__ import annotations

from decimal import Decimal

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User
from bot.repositories import AccountsRepository, TransactionsRepository
from bot.services import AccountsService

router = Router()


@router.message(Command("admin_accounts_by_user"))
async def admin_accounts_by_user(message: Message, user: User, session: AsyncSession) -> None:
    if not user.is_admin:
        await message.answer("Нет прав")
        return
    user_id = int(message.text.split()[1])
    accounts = await AccountsRepository(session).list_by_user(user_id)
    text = "\n".join([f"#{a.id} {a.account_number} {a.currency} {a.balance} {a.status}" for a in accounts]) or "нет"
    await message.answer(text)


@router.message(Command("admin_account_info"))
async def admin_account_info(message: Message, user: User, session: AsyncSession) -> None:
    if not user.is_admin:
        await message.answer("Нет прав")
        return
    account = await AccountsRepository(session).get_by_id(int(message.text.split()[1]))
    if account is None:
        await message.answer("Не найден")
        return
    await message.answer(f"#{account.id} {account.account_number}\n{account.currency} {account.balance}\n{account.status}")


@router.message(Command("admin_adjust_balance"))
async def admin_adjust_balance(message: Message, user: User, session: AsyncSession) -> None:
    if not user.is_admin:
        await message.answer("Нет прав")
        return
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer("Формат: /admin_adjust_balance <account_id> <amount> <comment>")
        return
    account = await AccountsRepository(session).get_by_id(int(parts[1]))
    if account is None:
        await message.answer("Счёт не найден")
        return
    amount = Decimal(parts[2])
    await AccountsService(AccountsRepository(session), TransactionsRepository(session)).adjust(account, amount, parts[3])
    await message.answer("Корректировка выполнена")
