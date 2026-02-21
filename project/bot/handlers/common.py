from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards.common import main_menu_kb

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message) -> None:
    await message.answer(
        "🏦 Добро пожаловать в DemoBank!\nВыберите действие в меню ниже.",
        reply_markup=main_menu_kb(),
    )


@router.callback_query(F.data == "menu:main")
async def menu_main(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Главное меню", reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "help:show")
async def show_help(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "ℹ️ Это демо-банк: счета, карты и переводы внутренние.\nРеальные деньги не используются.",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
