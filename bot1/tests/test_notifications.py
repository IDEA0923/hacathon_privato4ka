from datetime import datetime

import pytest

from services.notifications import build_notification_message, send_due_notifications


class FakeBot:
    def __init__(self) -> None:
        self.messages: list[tuple[int, str]] = []

    async def send_message(
        self,
        tg_id: int,
        text: str,
        disable_web_page_preview: bool = False,
    ) -> None:
        self.messages.append((tg_id, text))


class FakePg:
    def __init__(self, row: dict) -> None:
        self.row = row
        self.sent: set[tuple[int, int, str]] = set()

    async def get_due_notifications(self) -> list[dict]:
        key = (
            self.row["tg_id"],
            self.row["event_id"],
            self.row["notification_type"],
        )
        return [] if key in self.sent else [self.row]

    async def mark_notification_sent(
        self,
        tg_id: int,
        event_id: int,
        notification_type: str,
    ) -> bool:
        key = (tg_id, event_id, notification_type)
        if key in self.sent:
            return False
        self.sent.add(key)
        return True


def test_notification_message_uses_event_link() -> None:
    message = build_notification_message(
        {
            "notification_type": "week",
            "name_1": "Тестовая олимпиада",
            "event_subjects": "mat",
            "date_start": datetime(2026, 6, 2),
            "lnk": "https://example.com/olymp/1",
        }
    )

    assert "https://example.com/olymp/1" in message
    assert "Тестовая олимпиада" in message


def test_notification_message_handles_missing_link() -> None:
    message = build_notification_message(
        {
            "notification_type": "month",
            "name_1": "Тестовая олимпиада",
            "event_subjects": "inf",
            "date_start": datetime(2026, 6, 25),
            "lnk": "",
        }
    )

    assert "Ссылка пока недоступна" in message


@pytest.mark.asyncio
async def test_send_due_notifications_does_not_repeat(monkeypatch) -> None:
    row = {
        "tg_id": 1001,
        "event_id": 42,
        "notification_type": "day",
        "name_1": "Тестовая олимпиада",
        "event_subjects": "phy",
        "date_start": datetime(2026, 5, 27, 10, 30),
        "lnk": "https://example.com/olymp/42",
    }
    fake_pg = FakePg(row)
    fake_bot = FakeBot()
    monkeypatch.setattr("services.notifications.pg", fake_pg)

    assert await send_due_notifications(fake_bot) == 1
    assert await send_due_notifications(fake_bot) == 0
    assert len(fake_bot.messages) == 1
