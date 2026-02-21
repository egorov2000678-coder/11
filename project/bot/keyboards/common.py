from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Мой профиль", callback_data="profile:show")
    kb.button(text="Мои счета", callback_data="accounts:list")
    kb.button(text="Перевод", callback_data="transfer:start")
    kb.button(text="Мои карты", callback_data="cards:list")
    kb.button(text="Помощь", callback_data="help:show")
    kb.adjust(1)
    return kb.as_markup()
