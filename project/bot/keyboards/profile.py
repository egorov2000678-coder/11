from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def profile_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Мои счета", callback_data="accounts:list")
    kb.button(text="Вернуться в главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()
