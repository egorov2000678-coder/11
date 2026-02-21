from __future__ import annotations

from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.accounts import account_detail_kb, accounts_list_kb, open_account_currency_kb
from bot.models import User
from bot.repositories import AccountsRepository, TransactionsRepository
from bot.services import AccountsService

router = Router()


class AccountActionsStates(StatesGroup):
    entering_amount = State()


@router.callback_query(F.data == "accounts:list")
async def accounts_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    service = AccountsService(AccountsRepository(session), TransactionsRepository(session))
    accounts = await service.list_user_accounts(user.id)
    lines = ["💼 Ваши счета:"]
    for a in accounts:
        lines.append(f"• ****{a.account_number[-4:]} | {a.currency} | {a.balance} | {a.status}")
    if not accounts:
        lines.append("Счетов пока нет")
    await callback.message.edit_text("\n".join(lines), reply_markup=accounts_list_kb(accounts))
    await callback.answer()


@router.callback_query(F.data == "accounts:open")
async def accounts_open(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Выберите валюту нового счёта", reply_markup=open_account_currency_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("accounts:create:"))
async def accounts_create(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    currency = callback.data.split(":")[-1]
    service = AccountsService(AccountsRepository(session), TransactionsRepository(session))
    account = await service.open_account(user.id, currency)
    await callback.message.answer(f"Счёт создан: {account.account_number} ({account.currency})")
    await accounts_list(callback, user, session)


@router.callback_query(F.data.startswith("accounts:detail:"))
async def account_detail(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    account_id = int(callback.data.split(":")[-1])
    accounts_repo = AccountsRepository(session)
    tx_repo = TransactionsRepository(session)
    service = AccountsService(accounts_repo, tx_repo)
    account = await service.get_user_account(user.id, account_id)
    txs = await tx_repo.list_by_account(account.id, limit=5)
    hist = "\n".join([f"{t.type} {t.amount} {t.currency}" for t in txs]) or "Нет операций"
    text = f"Счёт: {account.account_number}\nБаланс: {account.balance} {account.currency}\nИстория:\n{hist}"
    await callback.message.edit_text(text, reply_markup=account_detail_kb(account.id))
    await callback.answer()


@router.callback_query(F.data.startswith("accounts:deposit:"))
async def ask_deposit(callback: CallbackQuery, state: FSMContext) -> None:
    account_id = int(callback.data.split(":")[-1])
    await state.update_data(action="deposit", account_id=account_id)
    await state.set_state(AccountActionsStates.entering_amount)
    await callback.message.answer("Введите сумму пополнения:")
    await callback.answer()


@router.callback_query(F.data.startswith("accounts:withdraw:"))
async def ask_withdraw(callback: CallbackQuery, state: FSMContext) -> None:
    account_id = int(callback.data.split(":")[-1])
    await state.update_data(action="withdraw", account_id=account_id)
    await state.set_state(AccountActionsStates.entering_amount)
    await callback.message.answer("Введите сумму снятия:")
    await callback.answer()


@router.message(StateFilter(AccountActionsStates.entering_amount))
async def do_amount(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    data = await state.get_data()
    await state.clear()
    try:
        amount = Decimal(message.text.strip())
        if amount <= 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError, AttributeError):
        await message.answer("Некорректная сумма")
        return

    service = AccountsService(AccountsRepository(session), TransactionsRepository(session))
    account = await service.get_user_account(user.id, int(data["account_id"]))
    if data["action"] == "deposit":
        await service.deposit(account, amount)
        await message.answer(f"Пополнение выполнено: +{amount} {account.currency}")
    else:
        await service.withdraw(account, amount)
        await message.answer(f"Снятие выполнено: -{amount} {account.currency}")
