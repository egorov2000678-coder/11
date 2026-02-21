from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.models import Account


def transfer_from_kb(accounts: list[Account]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for account in accounts:
        kb.button(text=f"{account.currency} ••••{account.account_number[-4:]}", callback_data=f"transfer:choose_from:{account.id}")
    kb.button(text="Отмена", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def transfer_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Подтвердить", callback_data="transfer:confirm")
    kb.button(text="Отмена", callback_data="menu:main")
    kb.adjust(2)
    return kb.as_markup()
