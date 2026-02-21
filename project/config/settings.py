from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    bot_token: str
    database_url: str
    admins: set[int]
    log_level: str



def _parse_admins(raw: str) -> set[int]:
    result: set[int] = set()
    for value in raw.split(","):
        value = value.strip()
        if not value:
            continue
        if value.lstrip("-").isdigit():
            result.add(int(value))
    return result



def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "")
    if not token:
        raise RuntimeError("BOT_TOKEN is required")

    return Settings(
        bot_token=token,
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bank.db"),
        admins=_parse_admins(os.getenv("ADMINS", "")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
