"""Точка входа парсера.

Поведение:
  1. Подключаемся к Postgres (asyncpg pool).
  2. Гарантируем наличие таблицы events (CREATE TABLE IF NOT EXISTS).
  3. По очереди проходим все источники из sources.ALL_SOURCES.
  4. Для каждого Event:
       - если md5(url) уже есть в events.lnk — пропускаем (дедуп);
       - иначе INSERT с обрезкой полей под VARCHAR.
  5. Печатаем сводку и выходим.

Запуск:
  docker compose --profile tools run --rm parser
или локально:
  POSTGRES_USER=... POSTGRES_PASSWORD=... POSTGRES_DB=... python main.py
"""

from __future__ import annotations

import asyncio
import logging
import sys

from db import DB
from sources import ALL_SOURCES
from sources.base import HttpClient

log = logging.getLogger("parser")


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
        stream=sys.stdout,
    )


async def run(per_source_limit: int = 50) -> int:
    db = DB()
    await db.connect()
    http = HttpClient()

    total_inserted = 0
    total_seen = 0
    try:
        for source_cls in ALL_SOURCES:
            source = source_cls()
            log.info("=== Источник: %s ===", source.name)
            inserted_here = 0
            seen_here = 0
            try:
                async for event in source.fetch(http, limit=per_source_limit):
                    seen_here += 1
                    try:
                        ok = await db.insert_event(event)
                    except Exception as e:
                        log.error("INSERT failed for %s: %s", event.url, e)
                        continue
                    if ok:
                        inserted_here += 1
                        log.info(
                            "+ %s | %s | %s | %s",
                            event.source,
                            event.name[:20],
                            event.date_start.date().isoformat(),
                            event.subjects or "-",
                        )
            except Exception as e:
                log.exception("Источник %s упал: %s", source.name, e)

            log.info(
                "Источник %s: увидено %d, записано %d",
                source.name, seen_here, inserted_here,
            )
            total_seen += seen_here
            total_inserted += inserted_here
    finally:
        await http.aclose()
        await db.close()

    log.info("ИТОГО: увидено %d, записано %d", total_seen, total_inserted)
    return total_inserted


def main() -> None:
    print("[+]start parsing")
    _setup_logging()
    try:
        inserted = asyncio.run(run())
    except KeyboardInterrupt:
        log.warning("прервано пользователем")
        sys.exit(130)
    except Exception as e:
        log.exception("парсер упал: %s", e)
        sys.exit(1)
    sys.exit(0 if inserted >= 0 else 1)


if __name__ == "__main__":
    main()
