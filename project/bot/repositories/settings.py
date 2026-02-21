from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Setting


class SettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, key: str) -> Setting | None:
        return await self.session.get(Setting, key)

    async def set(self, key: str, value: str) -> Setting:
        setting = await self.get(key)
        if setting is None:
            setting = Setting(key=key, value=value)
        else:
            setting.value = value
        self.session.add(setting)
        await self.session.flush()
        return setting
