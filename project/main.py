from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.handlers import accounts, cards, common, profile, transfers
from bot.handlers.admin import accounts as admin_accounts
from bot.handlers.admin import main as admin_main
from bot.handlers.admin import settings as admin_settings
from bot.handlers.admin import transactions as admin_transactions
from bot.handlers.admin import users as admin_users
from bot.middlewares import AuthMiddleware, DBSessionMiddleware, LoggingMiddleware
from bot.models import Base
from config import load_settings


async def main() -> None:
    settings = load_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))

    engine = create_async_engine(settings.database_url, future=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(DBSessionMiddleware(session_factory))
    dp.update.middleware(AuthMiddleware(settings))

    dp.include_router(common.router)
    dp.include_router(profile.router)
    dp.include_router(accounts.router)
    dp.include_router(transfers.router)
    dp.include_router(cards.router)

    dp.include_router(admin_main.router)
    dp.include_router(admin_users.router)
    dp.include_router(admin_accounts.router)
    dp.include_router(admin_transactions.router)
    dp.include_router(admin_settings.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
