from __future__ import annotations

import random
from decimal import Decimal

from bot.models import Account, AccountStatus, Transaction, TransactionType
from bot.repositories import AccountsRepository, TransactionsRepository


class AccountsService:
    def __init__(self, accounts_repo: AccountsRepository, tx_repo: TransactionsRepository) -> None:
        self.accounts_repo = accounts_repo
        self.tx_repo = tx_repo

    async def open_account(self, user_id: int, currency: str) -> Account:
        account_number = self._generate_account_number()
        account = Account(user_id=user_id, currency=currency.upper(), account_number=account_number)
        return await self.accounts_repo.save(account)

    async def list_user_accounts(self, user_id: int) -> list[Account]:
        return await self.accounts_repo.list_by_user(user_id)

    async def get_user_account(self, user_id: int, account_id: int) -> Account:
        account = await self.accounts_repo.get_by_id(account_id)
        if account is None or account.user_id != user_id:
            raise PermissionError("Счёт не найден или недоступен")
        return account

    async def deposit(self, account: Account, amount: Decimal, description: str = "Пополнение") -> Transaction:
        self._ensure_active(account)
        account.balance += amount
        tx = Transaction(
            from_account_id=None,
            to_account_id=account.id,
            amount=amount,
            currency=account.currency,
            type=TransactionType.DEPOSIT,
            description=description,
        )
        await self.accounts_repo.save(account)
        return await self.tx_repo.create(tx)

    async def withdraw(self, account: Account, amount: Decimal, description: str = "Снятие") -> Transaction:
        self._ensure_active(account)
        if account.balance < amount:
            raise ValueError("Недостаточно средств")
        account.balance -= amount
        tx = Transaction(
            from_account_id=account.id,
            to_account_id=None,
            amount=amount,
            currency=account.currency,
            type=TransactionType.WITHDRAW,
            description=description,
        )
        await self.accounts_repo.save(account)
        return await self.tx_repo.create(tx)

    async def adjust(self, account: Account, amount: Decimal, description: str) -> Transaction:
        account.balance += amount
        tx = Transaction(
            from_account_id=account.id if amount < 0 else None,
            to_account_id=account.id if amount > 0 else None,
            amount=abs(amount),
            currency=account.currency,
            type=TransactionType.ADJUSTMENT,
            description=description,
        )
        await self.accounts_repo.save(account)
        return await self.tx_repo.create(tx)

    @staticmethod
    def _ensure_active(account: Account) -> None:
        if account.status != AccountStatus.ACTIVE:
            raise ValueError("Операция недоступна для этого счёта")

    @staticmethod
    def _generate_account_number() -> str:
        return "40817810" + "".join(str(random.randint(0, 9)) for _ in range(12))
