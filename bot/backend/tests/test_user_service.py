import pytest

from app.services.users import UserService


pytestmark = pytest.mark.asyncio


async def test_get_or_create_is_idempotent(user_service: UserService) -> None:
    first = await user_service.get_or_create(
        tg_id=1, username="alice", first_name="Alice"
    )
    second = await user_service.get_or_create(
        tg_id=1, username="alice", first_name="Alice"
    )
    assert first.tg_id == second.tg_id == 1
    assert second.username == "alice"


async def test_get_or_create_updates_profile_fields(user_service: UserService) -> None:
    await user_service.get_or_create(tg_id=2, username="old", first_name="Old")
    updated = await user_service.get_or_create(
        tg_id=2, username="new", first_name="New", last_name="Last"
    )
    assert updated.username == "new"
    assert updated.first_name == "New"
    assert updated.last_name == "Last"


async def test_set_consent_sets_timestamp(user_service: UserService) -> None:
    await user_service.get_or_create(tg_id=3)
    user = await user_service.set_consent(tg_id=3)
    assert user.consent_at is not None


async def test_set_email_persists_value(user_service: UserService) -> None:
    await user_service.get_or_create(tg_id=4)
    user = await user_service.set_email(tg_id=4, email="user@example.com")
    assert user.email == "user@example.com"


async def test_set_email_for_unknown_user_raises(user_service: UserService) -> None:
    with pytest.raises(ValueError):
        await user_service.set_email(tg_id=999, email="user@example.com")


async def test_save_profile_normalizes_values(user_service: UserService) -> None:
    user = await user_service.save_profile(
        tg_id=5,
        subjects=[" math ", "physics", "math"],
        class_value="10",
        region="Moscow",
    )

    assert user.subjects == "matphy"
    assert user.class_ == 10
    assert user.region == "mos"
