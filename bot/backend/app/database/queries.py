from __future__ import annotations

import calendar
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
import sqlite3

from app.models.event import Event
from app.models.user import User
from app.utils.profile import subjects_match


DatabasePath = str | Path


def initialize_database(db_path: DatabasePath) -> None:
    path = _normalize_db_path(db_path)
    _ensure_parent_dir(path)

    with _connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                consent_at TEXT,
                subjects TEXT,
                "class" INTEGER,
                region TEXT
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subjects TEXT NOT NULL,
                "class" INTEGER NOT NULL,
                region TEXT NOT NULL,
                event_date TEXT NOT NULL,
                description TEXT,
                link TEXT
            );
            """
        )


def upsert_user(db_path: DatabasePath, user: User) -> User:
    initialize_database(db_path)

    existing = get_user_by_tg_id(db_path, user.tg_id)
    with _connect(db_path) as connection:
        if existing is None:
            cursor = connection.execute(
                """
                INSERT INTO users (
                    tg_id, username, first_name, last_name, email,
                    consent_at, subjects, "class", region
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                _user_values(user),
            )
            user_id = int(cursor.lastrowid)
        else:
            user_id = existing.id
            connection.execute(
                """
                UPDATE users
                SET username = ?,
                    first_name = ?,
                    last_name = ?,
                    email = ?,
                    consent_at = ?,
                    subjects = ?,
                    "class" = ?,
                    region = ?
                WHERE tg_id = ?
                """,
                (
                    user.username,
                    user.first_name,
                    user.last_name,
                    str(user.email) if user.email is not None else None,
                    _datetime_to_db(user.consent_at),
                    user.subjects,
                    user.class_,
                    user.region,
                    user.tg_id,
                ),
            )

    return user.model_copy(update={"id": user_id})


def save_or_update_user(
    db_path: DatabasePath,
    *,
    tg_id: int,
    subjects: str,
    class_value: int,
    region: str,
) -> User:
    initialize_database(db_path)

    existing = get_user_by_tg_id(db_path, tg_id)
    if existing is None:
        user = User(
            tg_id=tg_id,
            subjects=subjects,
            class_=class_value,
            region=region,
        )
    else:
        user = existing.model_copy(
            update={
                "subjects": subjects,
                "class_": class_value,
                "region": region,
            }
        )
    return upsert_user(db_path, user)


def get_user_by_tg_id(db_path: DatabasePath, tg_id: int) -> User | None:
    initialize_database(db_path)

    with _connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT id, tg_id, username, first_name, last_name, email,
                   consent_at, subjects, "class", region
            FROM users
            WHERE tg_id = ?
            """,
            (tg_id,),
        ).fetchone()

    if row is None:
        return None
    return _row_to_user(row)


def save_event(db_path: DatabasePath, event: Event) -> Event:
    initialize_database(db_path)

    with _connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO events (
                title, subjects, "class", region, event_date, description, link
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.title,
                event.subjects,
                event.class_,
                event.region,
                event.event_date.isoformat(),
                event.description,
                event.link,
            ),
        )
        event_id = int(cursor.lastrowid)

    return event.model_copy(update={"id": event_id})


def find_matching_events_for_user(
    db_path: DatabasePath,
    *,
    tg_id: int | None = None,
    user: User | None = None,
    today: date | None = None,
) -> list[Event]:
    initialize_database(db_path)

    loaded_user = user
    if loaded_user is None and tg_id is not None:
        loaded_user = get_user_by_tg_id(db_path, tg_id)
    if loaded_user is None or not _user_has_matching_data(loaded_user):
        return []

    start_date = today or date.today()
    end_date = _add_one_month(start_date)

    with _connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, title, subjects, "class", region, event_date, description, link
            FROM events
            WHERE "class" = ?
              AND region = ?
              AND date(event_date) >= date(?)
              AND date(event_date) <= date(?)
            ORDER BY date(event_date), title
            """,
            (
                loaded_user.class_,
                loaded_user.region,
                start_date.isoformat(),
                end_date.isoformat(),
            ),
        ).fetchall()

    return [
        event
        for event in (_row_to_event(row) for row in rows)
        if subjects_match(event.subjects, loaded_user.subjects)
    ]


@contextmanager
def _connect(db_path: DatabasePath) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def _normalize_db_path(db_path: DatabasePath) -> DatabasePath:
    if str(db_path) == ":memory:":
        return db_path
    return Path(db_path)


def _ensure_parent_dir(db_path: DatabasePath) -> None:
    if str(db_path) == ":memory:":
        return
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)


def _user_values(user: User) -> tuple[object, ...]:
    return (
        user.tg_id,
        user.username,
        user.first_name,
        user.last_name,
        str(user.email) if user.email is not None else None,
        _datetime_to_db(user.consent_at),
        user.subjects,
        user.class_,
        user.region,
    )


def _datetime_to_db(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        id=row["id"],
        tg_id=row["tg_id"],
        username=row["username"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
        consent_at=row["consent_at"],
        subjects=row["subjects"],
        class_=row["class"],
        region=row["region"],
    )


def _row_to_event(row: sqlite3.Row) -> Event:
    return Event(
        id=row["id"],
        title=row["title"],
        subjects=row["subjects"],
        class_=row["class"],
        region=row["region"],
        event_date=date.fromisoformat(str(row["event_date"])[:10]),
        description=row["description"],
        link=row["link"],
    )


def _user_has_matching_data(user: User) -> bool:
    return bool(user.subjects and user.class_ is not None and user.region)


def _add_one_month(value: date) -> date:
    month = value.month + 1
    year = value.year
    if month > 12:
        month = 1
        year += 1

    last_day = calendar.monthrange(year, month)[1]
    return value.replace(year=year, month=month, day=min(value.day, last_day))
