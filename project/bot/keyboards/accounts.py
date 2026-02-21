from bot.models import Account
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


CURRENCIES = ["RUB", "USD", "EUR", "TON"]


def accounts_list_kb(accounts: list[Account]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for account in accounts:
        kb.button(text=f"Подробнее {account.currency} ••••{account.account_number[-4:]}", callback_data=f"accounts:detail:{account.id}")
    kb.button(text="Открыть новый счёт", callback_data="accounts:open")
    kb.button(text="Главное меню", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def open_account_currency_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cur in CURRENCIES:
        kb.button(text=cur, callback_data=f"accounts:create:{cur}")
    kb.button(text="Назад", callback_data="accounts:list")
    kb.adjust(2)
    return kb.as_markup()


def account_detail_kb(account_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Пополнить счёт", callback_data=f"accounts:deposit:{account_id}")
    kb.button(text="Снять со счёта", callback_data=f"accounts:withdraw:{account_id}")
    kb.button(text="Перевести с этого счёта", callback_data=f"transfer:from:{account_id}")
    kb.button(text="Выпустить виртуальную карту", callback_data=f"cards:issue:{account_id}")
    kb.button(text="Назад", callback_data="accounts:list")
    kb.adjust(1)
    return kb.as_markup()
