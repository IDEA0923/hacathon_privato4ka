from datetime import date
import sqlite3

from app.database import queries
from app.models.event import Event
from app.utils.profile import (
    build_subjects_code,
    normalize_region_code,
    parse_class,
)


def test_subjects_code_uses_first_three_letters() -> None:
    assert build_subjects_code("math") == "mat"


def test_subjects_code_joins_multiple_subjects() -> None:
    assert build_subjects_code(["math", "physics"]) == "matphy"


def test_subjects_code_does_not_duplicate_repeated_subjects() -> None:
    assert build_subjects_code([" math ", "Math", "physics"]) == "matphy"


def test_class_is_parsed_as_int() -> None:
    assert parse_class("10") == 10


def test_region_uses_first_three_letters() -> None:
    assert normalize_region_code(" Primorsky ") == "pri"


def test_save_or_update_user_updates_same_tg_id_without_duplicates(tmp_path) -> None:
    db_path = tmp_path / "bot.sqlite3"

    first = queries.save_or_update_user(
        db_path,
        tg_id=100,
        subjects="mat",
        class_value=10,
        region="mos",
    )
    second = queries.save_or_update_user(
        db_path,
        tg_id=100,
        subjects="phy",
        class_value=11,
        region="pri",
    )

    with sqlite3.connect(db_path) as connection:
        users_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    assert second.id == first.id
    assert users_count == 1
    assert second.subjects == "phy"
    assert second.class_ == 11
    assert second.region == "pri"


def test_find_matching_events_returns_only_relevant_events(tmp_path) -> None:
    db_path = tmp_path / "bot.sqlite3"
    today = date(2026, 5, 24)
    queries.save_or_update_user(
        db_path,
        tg_id=200,
        subjects="matphy",
        class_value=10,
        region="mos",
    )
    for event in [
        Event(
            title="Math today",
            subjects="mat",
            class_=10,
            region="mos",
            event_date=today,
        ),
        Event(
            title="Physics boundary",
            subjects="phy",
            class_=10,
            region="mos",
            event_date=date(2026, 6, 24),
        ),
        Event(
            title="Wrong subject",
            subjects="inf",
            class_=10,
            region="mos",
            event_date=today,
        ),
        Event(
            title="Wrong class",
            subjects="mat",
            class_=9,
            region="mos",
            event_date=today,
        ),
        Event(
            title="Wrong region",
            subjects="mat",
            class_=10,
            region="pri",
            event_date=today,
        ),
        Event(
            title="Past event",
            subjects="mat",
            class_=10,
            region="mos",
            event_date=date(2026, 5, 23),
        ),
        Event(
            title="Too late",
            subjects="mat",
            class_=10,
            region="mos",
            event_date=date(2026, 6, 25),
        ),
    ]:
        queries.save_event(db_path, event)

    events = queries.find_matching_events_for_user(
        db_path,
        tg_id=200,
        today=today,
    )

    assert [event.title for event in events] == ["Math today", "Physics boundary"]
