from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for label in ["Пользователи", "Счета", "Транзакции", "Настройки"]:
        kb.button(text=label, callback_data="admin:info")
    kb.adjust(1)
    return kb.as_markup()
