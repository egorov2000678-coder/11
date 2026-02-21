from __future__ import annotations

from decimal import Decimal

from bot.models import Account, AccountStatus, Transaction, TransactionType
from bot.repositories import AccountsRepository, TransactionsRepository


class PaymentService:
    def __init__(self, accounts_repo: AccountsRepository, tx_repo: TransactionsRepository) -> None:
        self.accounts_repo = accounts_repo
        self.tx_repo = tx_repo

    async def transfer(self, from_account: Account, to_account: Account, amount: Decimal, description: str) -> tuple[Transaction, Transaction]:
        if from_account.status != AccountStatus.ACTIVE or to_account.status != AccountStatus.ACTIVE:
            raise ValueError("Один из счетов неактивен")
        if from_account.currency != to_account.currency:
            raise ValueError("Валюты счетов должны совпадать")
        if from_account.balance < amount:
            raise ValueError("Недостаточно средств")

        from_account.balance -= amount
        to_account.balance += amount

        out_tx = Transaction(
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            amount=amount,
            currency=from_account.currency,
            type=TransactionType.TRANSFER_OUT,
            description=description,
        )
        in_tx = Transaction(
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            amount=amount,
            currency=to_account.currency,
            type=TransactionType.TRANSFER_IN,
            description=description,
        )
        await self.accounts_repo.save(from_account)
        await self.accounts_repo.save(to_account)
        return await self.tx_repo.create(out_tx), await self.tx_repo.create(in_tx)
