"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_banned", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("balance", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.Enum("ACTIVE", "BLOCKED", "CLOSED", name="accountstatus"), nullable=False),
        sa.Column("account_number", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_accounts_account_number", "accounts", ["account_number"], unique=True)

    op.create_table(
        "cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("card_number", sa.String(length=16), nullable=False),
        sa.Column("holder_name", sa.String(length=64), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "BLOCKED", name="cardstatus"), nullable=False),
        sa.Column("expiry_month", sa.String(length=2), nullable=False),
        sa.Column("expiry_year", sa.String(length=2), nullable=False),
        sa.Column("cvv", sa.String(length=3), nullable=False),
        sa.Column("card_type", sa.Enum("VIRTUAL", "PHYSICAL", name="cardtype"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_cards_card_number", "cards", ["card_number"], unique=True)

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("from_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("to_account_id", sa.Integer(), sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column(
            "type",
            sa.Enum("DEPOSIT", "WITHDRAW", "TRANSFER_IN", "TRANSFER_OUT", "ADJUSTMENT", name="transactiontype"),
            nullable=False,
        ),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "settings",
        sa.Column("key", sa.String(length=100), primary_key=True),
        sa.Column("value", sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("settings")
    op.drop_table("transactions")
    op.drop_index("ix_cards_card_number", table_name="cards")
    op.drop_table("cards")
    op.drop_index("ix_accounts_account_number", table_name="accounts")
    op.drop_table("accounts")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
