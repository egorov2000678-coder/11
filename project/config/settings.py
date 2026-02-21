from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


@dataclass(slots=True)
class Settings:
    bot_token: str
    database_url: str
    database_sslmode: str | None
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

    raw_database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bank.db")
    database_url, sslmode = _normalize_database_url(raw_database_url)

    return Settings(
        bot_token=token,
        database_url=database_url,
        database_sslmode=sslmode,
        admins=_parse_admins(os.getenv("ADMINS", "")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )


def _normalize_database_url(database_url: str) -> tuple[str, str | None]:
    """Normalize provider URL formats and extract sslmode for asyncpg connect_args."""
    normalized = database_url
    if normalized.startswith("postgres://"):
        normalized = normalized.replace("postgres://", "postgresql+asyncpg://", 1)
    elif normalized.startswith("postgresql://"):
        normalized = normalized.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlsplit(normalized)
    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    sslmode = query_params.pop("sslmode", None)
    cleaned_query = urlencode(query_params)
    cleaned_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, cleaned_query, parsed.fragment))
    return cleaned_url, sslmode
