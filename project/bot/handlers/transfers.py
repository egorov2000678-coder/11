from __future__ import annotations

from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.fsm.transfers import TransfersStates
from bot.keyboards.transfers import transfer_confirm_kb, transfer_from_kb
from bot.models import User
from bot.repositories import AccountsRepository, TransactionsRepository, UsersRepository
from bot.services import AccountsService, PaymentService

router = Router()


@router.callback_query(F.data == "transfer:start")
async def transfer_start(callback: CallbackQuery, user: User, session: AsyncSession, state: FSMContext) -> None:
    accounts = await AccountsService(AccountsRepository(session), TransactionsRepository(session)).list_user_accounts(user.id)
    await state.set_state(TransfersStates.choosing_from)
    await callback.message.edit_text("Выберите счёт отправителя", reply_markup=transfer_from_kb(accounts))
    await callback.answer()


@router.callback_query(F.data.startswith("transfer:from:"))
async def transfer_from_account(callback: CallbackQuery, state: FSMContext) -> None:
    account_id = int(callback.data.split(":")[-1])
    await state.set_state(TransfersStates.entering_to)
    await state.update_data(from_account_id=account_id)
    await callback.message.answer("Введите номер счёта получателя:")
    await callback.answer()


@router.callback_query(F.data.startswith("transfer:choose_from:"), TransfersStates.choosing_from)
async def transfer_choose_from(callback: CallbackQuery, state: FSMContext) -> None:
    account_id = int(callback.data.split(":")[-1])
    await state.update_data(from_account_id=account_id)
    await state.set_state(TransfersStates.entering_to)
    await callback.message.answer("Введите номер счёта получателя:")
    await callback.answer()


@router.message(TransfersStates.entering_to)
async def transfer_enter_to(message: Message, state: FSMContext) -> None:
    await state.update_data(to_account_number=message.text.strip())
    await state.set_state(TransfersStates.entering_amount)
    await message.answer("Введите сумму перевода:")


@router.message(TransfersStates.entering_amount)
async def transfer_enter_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = Decimal(message.text.strip())
        if amount <= 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        await message.answer("Некорректная сумма")
        return
    await state.update_data(amount=str(amount))
    await state.set_state(TransfersStates.entering_comment)
    await message.answer("Введите комментарий или '-' ")


@router.message(TransfersStates.entering_comment)
async def transfer_enter_comment(message: Message, state: FSMContext) -> None:
    comment = message.text.strip()
    await state.update_data(comment="" if comment == "-" else comment)
    data = await state.get_data()
    await state.set_state(TransfersStates.confirming)
    await message.answer(
        f"Подтвердите перевод:\nСо счёта ID {data['from_account_id']}\n"
        f"На счёт {data['to_account_number']}\nСумма {data['amount']}",
        reply_markup=transfer_confirm_kb(),
    )


@router.callback_query(F.data == "transfer:confirm", TransfersStates.confirming)
async def transfer_confirm(callback: CallbackQuery, state: FSMContext, user: User, session: AsyncSession) -> None:
    data = await state.get_data()
    await state.clear()
    accounts_repo = AccountsRepository(session)
    from_account = await accounts_repo.get_by_id(int(data["from_account_id"]))
    to_account = await accounts_repo.get_by_number(data["to_account_number"])
    if from_account is None or to_account is None or from_account.user_id != user.id:
        await callback.message.answer("Ошибка счёта")
        await callback.answer()
        return
    service = PaymentService(accounts_repo, TransactionsRepository(session))
    amount = Decimal(data["amount"])
    await service.transfer(from_account, to_account, amount, data.get("comment", ""))
    await callback.message.answer(f"✅ Перевод выполнен: {amount} {from_account.currency}")
    target_user = await UsersRepository(session).get_by_id(to_account.user_id)
    if target_user and target_user.telegram_id != user.telegram_id:
        await callback.bot.send_message(target_user.telegram_id, f"📥 Вам поступил перевод: +{amount} {to_account.currency}")
    await callback.answer()
