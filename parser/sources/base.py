"""Базовый класс источника + общий HTTP-клиент.

Каждый источник наследуется от BaseSource и реализует fetch(): AsyncIterator[Event].
Общий HttpClient следит за:
 - User-Agent;
 - таймаутом;
 - задержкой между запросами (politeness);
 - robots.txt (через urllib.robotparser, грузим один раз на хост).
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import AsyncIterator, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

import env
from db import Event

log = logging.getLogger("parser.sources")


class HttpClient:
    """Асинхронный HTTP-клиент с глобальной задержкой и robots.txt."""

    def __init__(
        self,
        user_agent: str = env.USER_AGENT,
        timeout: float = env.REQUEST_TIMEOUT,
        delay: float = env.REQUEST_DELAY,
    ) -> None:
        self._client = httpx.AsyncClient(
            headers={"User-Agent": user_agent},
            timeout=timeout,
            follow_redirects=True,
        )
        self._delay = delay
        self._last_request_at: float = 0.0
        self._lock = asyncio.Lock()
        self._robots: dict[str, RobotFileParser] = {}
        self._user_agent = user_agent

    async def _robots_allows(self, url: str) -> bool:
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        rp = self._robots.get(host)
        if rp is None:
            rp = RobotFileParser()
            robots_url = f"{host}/robots.txt"
            try:
                r = await self._client.get(robots_url)
                if r.status_code == 200:
                    rp.parse(r.text.splitlines())
                else:
                    # Нет robots.txt — считаем, что разрешено.
                    rp.parse([])
            except Exception as e:
                log.warning("robots.txt fetch failed for %s: %s", host, e)
                rp.parse([])
            self._robots[host] = rp
        return rp.can_fetch(self._user_agent, url)

    async def get(self, url: str) -> Optional[str]:
        """GET с задержкой и проверкой robots. Возвращает текст или None при ошибке."""
        if not await self._robots_allows(url):
            log.info("robots.txt disallows %s", url)
            return None
        async with self._lock:
            now = time.monotonic()
            wait = self._delay - (now - self._last_request_at)
            if wait > 0:
                await asyncio.sleep(wait)
            try:
                resp = await self._client.get(url)
            except Exception as e:
                log.warning("GET %s failed: %s", url, e)
                self._last_request_at = time.monotonic()
                return None
            self._last_request_at = time.monotonic()
        if resp.status_code != 200:
            log.warning("GET %s -> HTTP %d", url, resp.status_code)
            return None
        return resp.text

    async def aclose(self) -> None:
        await self._client.aclose()


class BaseSource:
    """Базовый класс источника.

    Подклассы переопределяют:
      - name: короткое имя (≤20 симв., пойдёт в events.frm);
      - fetch(http, limit): асинхронный генератор Event'ов.
    """

    name: str = "base"

    async def fetch(
        self, http: HttpClient, limit: int = 50
    ) -> AsyncIterator[Event]:
        if False:
            yield  # pragma: no cover
        raise NotImplementedError
