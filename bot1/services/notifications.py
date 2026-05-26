import asyncio
import html
import logging
from datetime import datetime
from typing import Any

from aiogram import Bot

from dbs_div import pg
from services.users import subject_codes_to_labels

log = logging.getLogger(__name__)


def _get(row: Any, key: str, default: Any = None) -> Any:
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        return row[key]
    except (KeyError, TypeError):
        return default


def _format_date(value: Any, *, include_time: bool = False) -> str:
    if isinstance(value, datetime):
        if include_time and any((value.hour, value.minute, value.second)):
            return value.strftime("%d.%m.%Y %H:%M")
        return value.strftime("%d.%m.%Y")
    if value:
        return str(value)
    return "дата уточняется"


def _valid_link(value: Any) -> str | None:
    if not value:
        return None
    link = str(value).strip()
    if link.startswith(("https://", "http://")):
        return link
    return None


def build_notification_message(row: Any) -> str:
    notification_type = str(_get(row, "notification_type", "month"))
    name = html.escape(str(_get(row, "name_1", "Олимпиада")), quote=False)
    subject = html.escape(subject_codes_to_labels(_get(row, "event_subjects")), quote=False)
    date_start = _get(row, "date_start")
    link = _valid_link(_get(row, "lnk"))

    if notification_type == "week":
        lines = [
            f"⏰ До олимпиады «{name}» осталась неделя.",
            f"Предмет: {subject}.",
            f"Дата: {_format_date(date_start)}.",
            "",
            "Проверьте регистрацию или успейте зарегистрироваться и сохраните дату участия.",
        ]
    elif notification_type == "day":
        lines = [
            f"🚀 Уже завтра олимпиада «{name}».",
            f"Предмет: {subject}.",
            f"Дата: {_format_date(date_start, include_time=True)}.",
            "",
            "Подготовьте всё нужное для участия заранее.",
        ]
    else:
        lines = [
            f"📚 Через месяц состоится олимпиада по предмету: {subject}.",
            f"«{name}»",
            f"Дата: {_format_date(date_start)}.",
            "",
            "Уже можно посмотреть условия и начать подготовку.",
        ]

    if link is not None:
        lines.extend(["", f"🔗 Подробнее и регистрация: {html.escape(link, quote=False)}"])
    else:
        lines.extend(["", "🔗 Ссылка пока недоступна."])

    return "\n".join(lines)


async def send_due_notifications(bot: Bot) -> int:
    rows = await pg.get_due_notifications()
    sent = 0

    for row in rows:
        tg_id = int(_get(row, "tg_id"))
        event_id = int(_get(row, "event_id"))
        notification_type = str(_get(row, "notification_type"))
        message = build_notification_message(row)

        try:
            await bot.send_message(tg_id, message, disable_web_page_preview=False)
        except Exception as exc:
            log.warning(
                "Failed to send %s notification for event %s to %s: %s",
                notification_type,
                event_id,
                tg_id,
                exc,
            )
            continue

        if await pg.mark_notification_sent(tg_id, event_id, notification_type):
            sent += 1

    return sent


async def notification_worker(bot: Bot, interval_seconds: int = 60 * 60) -> None:
    while True:
        try:
            sent = await send_due_notifications(bot)
            if sent:
                log.info("Sent %d olympiad notifications", sent)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.exception("Notification check failed: %s", exc)

        await asyncio.sleep(interval_seconds)
