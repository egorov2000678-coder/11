from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards.admin import admin_menu_kb
from bot.models import User

router = Router()


@router.message(Command("admin"))
async def admin_menu(message: Message, user: User) -> None:
    if not user.is_admin:
        await message.answer("Доступ запрещён")
        return
    await message.answer("⚙️ Админ-панель", reply_markup=admin_menu_kb())
