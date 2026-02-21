from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.fsm.card_issue import CardIssueStates
from bot.models import CardStatus, User
from bot.repositories import AccountsRepository, CardsRepository
from bot.services import CardService

router = Router()


def _mask(card_number: str) -> str:
    return f"**** **** **** {card_number[-4:]}"


@router.callback_query(F.data == "cards:list")
async def cards_list(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    cards = await CardsRepository(session).list_by_user(user.id)
    if not cards:
        await callback.message.edit_text("У вас пока нет карт")
    else:
        text = "\n".join([f"{_mask(c.card_number)} | {c.status}" for c in cards])
        await callback.message.edit_text(f"💳 Ваши карты:\n{text}")
    await callback.answer()


@router.callback_query(F.data.startswith("cards:issue:"))
async def ask_issue(callback: CallbackQuery, state: FSMContext) -> None:
    account_id = int(callback.data.split(":")[-1])
    await state.update_data(account_id=account_id)
    await state.set_state(CardIssueStates.entering_holder_name)
    await callback.message.answer("Введите имя для карты (латиницей):")
    await callback.answer()


@router.message(CardIssueStates.entering_holder_name)
async def do_issue(message: Message, state: FSMContext, user: User, session: AsyncSession) -> None:
    data = await state.get_data()
    await state.clear()
    account = await AccountsRepository(session).get_by_id(int(data["account_id"]))
    if account is None or account.user_id != user.id:
        await message.answer("Счёт недоступен")
        return
    card = await CardService(CardsRepository(session)).issue_virtual(account, message.text.strip().upper())
    await message.answer(
        f"Карта выпущена\nНомер: {card.card_number}\nСрок: {card.expiry_month}/{card.expiry_year}\nCVV: {card.cvv}"
    )


@router.message(F.text.startswith("/card_block "))
async def block_card(message: Message, user: User, session: AsyncSession) -> None:
    card_id = int(message.text.split()[1])
    card = await CardsRepository(session).get_by_id(card_id)
    if card is None or card.account.user_id != user.id:
        await message.answer("Карта не найдена")
        return
    await CardService(CardsRepository(session)).set_status(card, CardStatus.BLOCKED)
    await message.answer("Карта заблокирована")


@router.message(F.text.startswith("/card_unblock "))
async def unblock_card(message: Message, user: User, session: AsyncSession) -> None:
    card_id = int(message.text.split()[1])
    card = await CardsRepository(session).get_by_id(card_id)
    if card is None or card.account.user_id != user.id:
        await message.answer("Карта не найдена")
        return
    await CardService(CardsRepository(session)).set_status(card, CardStatus.ACTIVE)
    await message.answer("Карта разблокирована")
