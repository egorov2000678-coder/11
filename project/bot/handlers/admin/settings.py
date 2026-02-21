from __future__ import annotations

from decimal import Decimal

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User
from bot.repositories import SettingsRepository
from bot.services import AppSettingsService

router = Router()


@router.message(Command("admin_commission_get"))
async def admin_commission_get(message: Message, user: User, session: AsyncSession) -> None:
    if not user.is_admin:
        await message.answer("Нет прав")
        return
    value = await AppSettingsService(SettingsRepository(session)).get_commission_percent()
    await message.answer(f"Комиссия: {value}%")


@router.message(Command("admin_commission_set"))
async def admin_commission_set(message: Message, user: User, session: AsyncSession) -> None:
    if not user.is_admin:
        await message.answer("Нет прав")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Формат: /admin_commission_set <percent>")
        return
    value = Decimal(parts[1])
    await AppSettingsService(SettingsRepository(session)).set_commission_percent(value)
    await message.answer("Комиссия обновлена")
