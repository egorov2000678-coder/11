from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Account, Transaction, User
from bot.repositories import UsersRepository

router = Router()


def _admin_guard(user: User) -> bool:
    return user.is_admin


@router.message(Command("admin_user_by_id"))
async def admin_user_by_id(message: Message, user: User, session: AsyncSession) -> None:
    if not _admin_guard(user):
        await message.answer("Нет прав")
        return
    parts = message.text.split()
    target = await UsersRepository(session).get_by_id(int(parts[1])) if len(parts) > 1 else None
    await _send_user_info(message, target, session)


@router.message(Command("admin_user_by_tid"))
async def admin_user_by_tid(message: Message, user: User, session: AsyncSession) -> None:
    if not _admin_guard(user):
        await message.answer("Нет прав")
        return
    parts = message.text.split()
    target = await UsersRepository(session).get_by_telegram_id(int(parts[1])) if len(parts) > 1 else None
    await _send_user_info(message, target, session)


@router.message(Command("admin_user_by_username"))
async def admin_user_by_username(message: Message, user: User, session: AsyncSession) -> None:
    if not _admin_guard(user):
        await message.answer("Нет прав")
        return
    parts = message.text.split(maxsplit=1)
    target = await UsersRepository(session).get_by_username(parts[1]) if len(parts) > 1 else None
    await _send_user_info(message, target, session)


@router.message(Command("admin_ban_user"))
async def admin_ban_user(message: Message, user: User, session: AsyncSession) -> None:
    if not _admin_guard(user):
        await message.answer("Нет прав")
        return
    target = await UsersRepository(session).get_by_id(int(message.text.split()[1]))
    if target is None:
        await message.answer("Пользователь не найден")
        return
    target.is_banned = True
    await session.flush()
    await message.answer("Пользователь заблокирован")


@router.message(Command("admin_unban_user"))
async def admin_unban_user(message: Message, user: User, session: AsyncSession) -> None:
    if not _admin_guard(user):
        await message.answer("Нет прав")
        return
    target = await UsersRepository(session).get_by_id(int(message.text.split()[1]))
    if target is None:
        await message.answer("Пользователь не найден")
        return
    target.is_banned = False
    await session.flush()
    await message.answer("Пользователь разблокирован")


async def _send_user_info(message: Message, target: User | None, session: AsyncSession) -> None:
    if target is None:
        await message.answer("Пользователь не найден")
        return
    accounts = await session.scalars(select(Account).where(Account.user_id == target.id))
    tx_count = await session.scalar(
        select(func.count(Transaction.id)).where(
            (Transaction.from_account_id.in_(select(Account.id).where(Account.user_id == target.id)))
            | (Transaction.to_account_id.in_(select(Account.id).where(Account.user_id == target.id)))
        )
    )
    account_lines = [f"{a.id}: {a.account_number} {a.currency} {a.balance}" for a in accounts]
    await message.answer(
        f"User #{target.id}\nTID: {target.telegram_id}\n@{target.username or '-'}\n"
        f"is_admin={target.is_admin}, banned={target.is_banned}\n"
        f"Счета:\n" + ("\n".join(account_lines) if account_lines else "нет") + f"\nTx: {tx_count or 0}"
    )
