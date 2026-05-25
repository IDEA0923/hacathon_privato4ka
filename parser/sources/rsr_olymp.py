"""Источник rsr-olymp.ru — Российский совет олимпиад школьников (РСОШ).

Парсим главный листинг олимпиад. У РСОШ каждая олимпиада имеет
уровень I/II/III — это пишем в поле events.lvl. Конкретный календарь
этапов лежит на странице каждой олимпиады; здесь, как и для olimpiada.ru,
мы делаем "лёгкий" обход листинга и, если точная дата не найдена в
карточке, ставим заглушку (сегодня + 30 дней), оставляя название/предметы
ради последующего ручного уточнения.
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

log = logging.getLogger("parser.rsr_olymp")

BASE_URL = "https://rsr-olymp.ru"
LISTING_URL = f"{BASE_URL}/olymp/list"

_LEVEL_RE = re.compile(r"\b([IVХ]{1,3})\s*уров", re.IGNORECASE)
_DATE_DOTS_RE = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")


def _parse_date(text: str) -> Optional[datetime]:
    if not text:
        return None
    m = _DATE_DOTS_RE.search(text)
    if not m:
        return None
    try:
        return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None


def _detect_level(text: str) -> str:
    if not text:
        return ""
    m = _LEVEL_RE.search(text)
    if not m:
        return ""
    return f"{m.group(1).upper()} уровень"


class RsrOlymp(BaseSource):
    name = "rsr-olymp.ru"

    async def fetch(
        self, http: HttpClient, limit: int = 50
    ) -> AsyncIterator[Event]:
        html = await http.get(LISTING_URL)
        if not html:
            # На случай, если структура URL поменялась, пробуем корень.
            html = await http.get(BASE_URL)
        if not html:
            log.warning("rsr-olymp.ru: пустой ответ")
            return

        tree = HTMLParser(html)
        seen_urls: set[str] = set()
        count = 0

        # Ссылки на конкретные олимпиады обычно содержат /olymp/<id> или /olympiad/.
        for a in tree.css("a"):
            href = a.attributes.get("href") or ""
            if not ("/olymp/" in href or "/olympiad/" in href):
                continue
            # Сама страница листинга — пропускаем.
            if href.rstrip("/").endswith("/list"):
                continue

            title = normalize(a.text())
            if not title or len(title) < 3:
                continue

            full_url = urljoin(BASE_URL, href.split("#")[0])
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            parent = a.parent
            ctx_text = normalize(parent.text()) if parent is not None else title

            subjects = detect_subjects(ctx_text) or detect_subjects(title)
            cs, ce = detect_classes(ctx_text)
            level = _detect_level(ctx_text)

            date_start = _parse_date(ctx_text) or (
                datetime.utcnow() + timedelta(days=30)
            )
            date_end = date_start + timedelta(days=1)

            yield Event(
                name=title,
                date_start=date_start,
                date_end=date_end,
                class_start=cs,
                class_end=ce,
                level=level,
                source=self.name,
                url=full_url,
                subjects=subjects,
                description=ctx_text or title,
            )

            count += 1
            if count >= limit:
                break

        log.info("rsr-olymp.ru: собрано %d записей", count)
