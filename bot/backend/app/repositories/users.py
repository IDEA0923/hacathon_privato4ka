import calendar
from datetime import date
from pathlib import Path
from typing import Protocol

from app.database import queries
from app.models.event import Event
from app.models.user import User
from app.utils.profile import subjects_match


class UserRepository(Protocol):
    async def get(self, tg_id: int) -> User | None: ...
    async def upsert(self, user: User) -> User: ...
    async def save_profile(
        self,
        tg_id: int,
        *,
        subjects: str,
        class_value: int,
        region: str,
    ) -> User: ...
    async def find_matching_events(
        self,
        tg_id: int,
        *,
        today: date | None = None,
    ) -> list[Event]: ...


class InMemoryUserRepository:
    """In-memory заглушка вместо реальной БД.

    Подходит для первого пользовательского сценария. Данные теряются
    при рестарте процесса — реальный репозиторий подключим позже.
    """

    def __init__(self) -> None:
        self._items: dict[int, User] = {}
        self._events: dict[int, Event] = {}
        self._next_user_id = 1
        self._next_event_id = 1

    async def get(self, tg_id: int) -> User | None:
        return self._items.get(tg_id)

    async def upsert(self, user: User) -> User:
        existing = self._items.get(user.tg_id)
        user_id = existing.id if existing is not None else user.id
        if user_id is None:
            user_id = self._next_user_id
            self._next_user_id += 1

        saved = user.model_copy(update={"id": user_id})
        self._items[saved.tg_id] = saved
        return saved

    async def save_profile(
        self,
        tg_id: int,
        *,
        subjects: str,
        class_value: int,
        region: str,
    ) -> User:
        user = self._items.get(tg_id)
        if user is None:
            user = User(tg_id=tg_id)

        updated = user.model_copy(
            update={
                "subjects": subjects,
                "class_": class_value,
                "region": region,
            }
        )
        return await self.upsert(updated)

    async def find_matching_events(
        self,
        tg_id: int,
        *,
        today: date | None = None,
    ) -> list[Event]:
        user = await self.get(tg_id)
        if user is None or not (user.subjects and user.class_ is not None and user.region):
            return []

        start_date = today or date.today()
        end_date = _add_one_month(start_date)
        return [
            event
            for event in sorted(
                self._events.values(),
                key=lambda item: (item.event_date, item.title),
            )
            if event.class_ == user.class_
            and event.region == user.region
            and start_date <= event.event_date <= end_date
            and subjects_match(event.subjects, user.subjects)
        ]

    async def add_event(self, event: Event) -> Event:
        event_id = event.id or self._next_event_id
        if event.id is None:
            self._next_event_id += 1

        saved = event.model_copy(update={"id": event_id})
        self._events[event_id] = saved
        return saved


class SQLiteUserRepository:
    def __init__(self, db_path: str | Path) -> None:
        self._db_path = db_path
        queries.initialize_database(self._db_path)

    async def get(self, tg_id: int) -> User | None:
        return queries.get_user_by_tg_id(self._db_path, tg_id)

    async def upsert(self, user: User) -> User:
        return queries.upsert_user(self._db_path, user)

    async def save_profile(
        self,
        tg_id: int,
        *,
        subjects: str,
        class_value: int,
        region: str,
    ) -> User:
        return queries.save_or_update_user(
            self._db_path,
            tg_id=tg_id,
            subjects=subjects,
            class_value=class_value,
            region=region,
        )

    async def find_matching_events(
        self,
        tg_id: int,
        *,
        today: date | None = None,
    ) -> list[Event]:
        return queries.find_matching_events_for_user(
            self._db_path,
            tg_id=tg_id,
            today=today,
        )


def _add_one_month(value: date) -> date:
    month = value.month + 1
    year = value.year
    if month > 12:
        month = 1
        year += 1

    last_day = calendar.monthrange(year, month)[1]
    return value.replace(year=year, month=month, day=min(value.day, last_day))
