from __future__ import annotations

from decimal import Decimal

from bot.repositories import SettingsRepository


class AppSettingsService:
    COMMISSION_KEY = "COMMISSION_PERCENT"

    def __init__(self, settings_repo: SettingsRepository) -> None:
        self.settings_repo = settings_repo

    async def get_commission_percent(self) -> Decimal:
        setting = await self.settings_repo.get(self.COMMISSION_KEY)
        return Decimal(setting.value) if setting else Decimal("0")

    async def set_commission_percent(self, percent: Decimal) -> Decimal:
        await self.settings_repo.set(self.COMMISSION_KEY, str(percent))
        return percent
