"""Источник olimpiada.ru — крупный агрегатор школьных олимпиад.

Парсим листинг /activities. Для каждой карточки читаем:
  - название (заголовок ссылки),
  - URL предметной/мероприятийной страницы,
  - текст карточки (для извлечения предметов, классов и описания).

Дату ближайшего этапа берём из текста карточки по простому регулярному
выражению "ДД.ММ.ГГГГ" / "ДД месяц ГГГГ". Если не нашли — ставим
сегодня + 30 дней (чтобы запись всё-таки попала в БД и было видно
в календаре, что точная дата требует уточнения у источника).
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import AsyncIterator, Optional
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from classes import detect_classes
from db import Event
from subjects import detect_subjects, normalize

from .base import BaseSource, HttpClient

log = logging.getLogger("parser.olimpiada_ru")

BASE_URL = "https://olimpiada.ru"
LISTING_URL = f"{BASE_URL}/activities"

_RU_MONTHS = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
    "мая": 5, "июня": 6, "июля": 7, "августа": 8,
    "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12,
}

_DATE_DOTS_RE = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")
_DATE_RU_RE = re.compile(
    r"\b(\d{1,2})\s+("
    + "|".join(_RU_MONTHS.keys())
    + r")\s+(\d{4})\b",
    re.IGNORECASE,
)


def _parse_date(text: str) -> Optional[datetime]:
    if not text:
        return None
    m = _DATE_DOTS_RE.search(text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime(y, mo, d)
        except ValueError:
            return None
    m = _DATE_RU_RE.search(text)
    if m:
        d = int(m.group(1))
        mo = _RU_MONTHS[m.group(2).lower()]
        y = int(m.group(3))
        try:
            return datetime(y, mo, d)
        except ValueError:
            return None
    return None


class OlimpiadaRu(BaseSource):
    name = "olimpiada.ru"

    async def fetch(
        self, http: HttpClient, limit: int = 50
    ) -> AsyncIterator[Event]:
        html = await http.get(LISTING_URL)
        if not html:
            log.warning("olimpiada.ru: пустой ответ от %s", LISTING_URL)
            return

        tree = HTMLParser(html)

        # На olimpiada.ru карточка активности — ссылка на /activity/<id>.
        # Выгребаем ВСЕ такие ссылки и дедуплицируем по href.
        seen_urls: set[str] = set()
        count = 0

        for a in tree.css("a"):
            href = a.attributes.get("href") or ""
            if "/activity/" not in href:
                continue
            title = normalize(a.text())
            if not title or len(title) < 3:
                continue

            full_url = urljoin(BASE_URL, href.split("#")[0])
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            # Контекст вокруг ссылки — используем родительский блок как описание.
            parent = a.parent
            ctx_text = normalize(parent.text()) if parent is not None else title

            subjects = detect_subjects(ctx_text) or detect_subjects(title)
            cs, ce = detect_classes(ctx_text)

            date_start = _parse_date(ctx_text) or (
                datetime.utcnow() + timedelta(days=30)
            )
            date_end = date_start + timedelta(days=1)

            description = ctx_text or title

            yield Event(
                name=title,
                date_start=date_start,
                date_end=date_end,
                class_start=cs,
                class_end=ce,
                level="",
                source=self.name,
                url=full_url,
                subjects=subjects,
                description=description,
            )

            count += 1
            if count >= limit:
                break

        log.info("olimpiada.ru: собрано %d записей", count)
