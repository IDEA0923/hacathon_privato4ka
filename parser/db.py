"""Слой доступа к Postgres для парсера.

Пишем в существующую таблицу `events` (схема — см. init.sql).
Если таблицы нет (init.sql сейчас с синтаксической ошибкой и
не создаёт events) — создаём её сами через CREATE TABLE IF NOT EXISTS.
Сам init.sql при этом не трогаем.

Дедупликация — по md5(url): храним хэш в колонке `lnk VARCHAR(40)`.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import asyncpg

import env

log = logging.getLogger("parser.db")


# Схема, совместимая с тем, что описано в init.sql.
# Используем IF NOT EXISTS — если таблица уже есть, ничего не меняем.
_CREATE_EVENTS_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    name_1 VARCHAR(20),
    date_start TIMESTAMP DEFAULT NOW() + INTERVAL '3 days',
    date_end TIMESTAMP DEFAULT NOW() + INTERVAL '4 days',
    class_start INT DEFAULT 0,
    class_end INT DEFAULT 11,
    lvl VARCHAR(20),
    frm VARCHAR(20),
    lnk VARCHAR(40),
    subjects VARCHAR(20),
    description_1 VARCHAR(500)
)
"""

_INSERT_SQL = """
INSERT INTO events
    (name_1, date_start, date_end, class_start, class_end,
     lvl, frm, lnk, subjects, description_1)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
"""

_EXISTS_SQL = "SELECT 1 FROM events WHERE lnk = $1 LIMIT 1"


@dataclass
class Event:
    """Один распарсенный пункт. Поля уже подогнаны под VARCHAR-ограничения."""
    name: str                   # до 20 симв.
    date_start: datetime
    date_end: Optional[datetime]
    class_start: int
    class_end: int
    level: str                  # до 20 симв.
    source: str                 # до 20 симв. (frm)
    url: str                    # полный URL (в БД пойдёт md5)
    subjects: str               # до 20 симв., коды
    description: str            # до 500 симв.


def url_hash(url: str) -> str:
    """md5(url) hex — 32 символа, влезает в VARCHAR(40)."""
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def _clip(s: Optional[str], n: int) -> str:
    if not s:
        return ""
    s = s.strip()
    return s if len(s) <= n else s[:n]


class DB:
    """Тонкая обёртка над asyncpg.Pool."""

    def __init__(self) -> None:
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(
            user=env.POSTGRES_USER,
            password=env.POSTGRES_PASSWORD,
            database=env.POSTGRES_DB,
            host=env.POSTGRES_HOST,
            port=env.POSTGRES_PORT,
            min_size=1,
            max_size=4,
        )
        async with self._pool.acquire() as conn:
            await conn.execute(_CREATE_EVENTS_SQL)
        log.info("DB connected, events table ensured")

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def exists(self, url: str) -> bool:
        assert self._pool is not None, "DB not connected"
        h = url_hash(url)
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(_EXISTS_SQL, h)
            return row is not None

    async def insert_event(self, ev: Event) -> bool:
        """Вставляет событие. Возвращает True если вставили, False если дубль."""
        assert self._pool is not None, "DB not connected"
        h = url_hash(ev.url)
        async with self._pool.acquire() as conn:
            exists = await conn.fetchrow(_EXISTS_SQL, h)
            if exists is not None:
                return False
            await conn.execute(
                _INSERT_SQL,
                _clip(ev.name, 20),
                ev.date_start,
                ev.date_end,
                int(ev.class_start),
                int(ev.class_end),
                _clip(ev.level, 20),
                _clip(ev.source, 20),
                h,
                _clip(ev.subjects, 20),
                _clip(ev.description, 500),
            )
            return True
