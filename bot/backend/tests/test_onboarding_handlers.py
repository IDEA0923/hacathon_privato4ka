from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.handlers.onboarding import (
    handle_consent_agree,
    handle_consent_decline,
    handle_class_input,
    handle_email_input,
    handle_email_skip,
    handle_region_input,
    handle_subjects_input,
)
from app.handlers.start import handle_start
from app.models.event import Event
from app.repositories.users import InMemoryUserRepository
from app.services.users import UserService
from app.states.onboarding import OnboardingStates


pytestmark = pytest.mark.asyncio


def _make_message(
    text: str | None = None,
    user_id: int = 100,
    username: str | None = "tester",
    first_name: str | None = "Test",
):
    message = MagicMock()
    message.text = text
    message.from_user = SimpleNamespace(
        id=user_id,
        username=username,
        first_name=first_name,
        last_name=None,
    )
    message.answer = AsyncMock()
    return message


def _make_callback(data: str, user_id: int = 100):
    callback = MagicMock()
    callback.data = data
    callback.from_user = SimpleNamespace(id=user_id)
    callback.message = MagicMock()
    callback.message.answer = AsyncMock()
    callback.message.edit_reply_markup = AsyncMock()
    callback.answer = AsyncMock()
    return callback


def _make_state(initial_data: dict | None = None):
    data = dict(initial_data or {})

    async def update_data(**kwargs):
        data.update(kwargs)
        return data

    async def get_data():
        return data

    state = MagicMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    state.update_data = AsyncMock(side_effect=update_data)
    state.get_data = AsyncMock(side_effect=get_data)
    return state


async def test_start_creates_user_and_sets_state(user_service: UserService) -> None:
    message = _make_message()
    state = _make_state()

    await handle_start(message, state, user_service)

    saved = await user_service.get(100)
    assert saved is not None
    assert saved.username == "tester"
    state.set_state.assert_awaited_once_with(OnboardingStates.waiting_consent)
    message.answer.assert_awaited_once()


async def test_consent_agree_sets_consent_and_moves_to_subjects(
    user_service: UserService,
) -> None:
    await user_service.get_or_create(tg_id=100, username="tester")
    callback = _make_callback("consent:agree")
    state = _make_state()

    await handle_consent_agree(callback, state, user_service)

    saved = await user_service.get(100)
    assert saved is not None and saved.consent_at is not None
    state.set_state.assert_awaited_once_with(OnboardingStates.waiting_subjects)
    callback.message.answer.assert_awaited_once()
    callback.answer.assert_awaited_once()


async def test_consent_decline_clears_state() -> None:
    callback = _make_callback("consent:decline")
    state = _make_state()

    await handle_consent_decline(callback, state)

    state.clear.assert_awaited_once()
    callback.message.answer.assert_awaited_once()
    callback.answer.assert_awaited_once()


async def test_email_input_valid_saves_and_clears_state(
    user_service: UserService,
) -> None:
    await user_service.get_or_create(tg_id=100)
    message = _make_message(text="user@example.com")
    state = _make_state()

    await handle_email_input(message, state, user_service)

    saved = await user_service.get(100)
    assert saved is not None and saved.email == "user@example.com"
    state.clear.assert_awaited_once()
    assert message.answer.await_count == 2


async def test_email_input_invalid_does_not_clear_state(
    user_service: UserService,
) -> None:
    await user_service.get_or_create(tg_id=100)
    message = _make_message(text="not-an-email")
    state = _make_state()

    await handle_email_input(message, state, user_service)

    saved = await user_service.get(100)
    assert saved is not None and saved.email is None
    state.clear.assert_not_called()
    message.answer.assert_awaited_once()


async def test_subjects_input_moves_to_class_state() -> None:
    message = _make_message(text="math, physics")
    state = _make_state()

    await handle_subjects_input(message, state)

    state.update_data.assert_awaited_once_with(subjects="math, physics")
    state.set_state.assert_awaited_once_with(OnboardingStates.waiting_class)
    message.answer.assert_awaited_once()


async def test_class_input_moves_to_region_state() -> None:
    message = _make_message(text="10")
    state = _make_state()

    await handle_class_input(message, state)

    state.update_data.assert_awaited_once_with(class_value="10")
    state.set_state.assert_awaited_once_with(OnboardingStates.waiting_region)
    message.answer.assert_awaited_once()


async def test_region_input_saves_profile_and_shows_events(
    user_service: UserService,
    repository: InMemoryUserRepository,
) -> None:
    await user_service.get_or_create(tg_id=100)
    await repository.add_event(
        Event(
            title="Math contest",
            subjects="mat",
            class_=10,
            region="mos",
            event_date=date.today(),
        )
    )
    message = _make_message(text="Moscow")
    state = _make_state({"subjects": "math, physics", "class_value": "10"})

    await handle_region_input(message, state, user_service)

    saved = await user_service.get(100)
    assert saved is not None
    assert saved.subjects == "matphy"
    assert saved.class_ == 10
    assert saved.region == "mos"
    state.set_state.assert_awaited_once_with(OnboardingStates.waiting_email)
    assert message.answer.await_count == 2
    assert "Math contest" in message.answer.await_args_list[0].args[0]


async def test_email_skip_clears_state_and_shows_webapp() -> None:
    message = _make_message(text="Пропустить")
    state = _make_state()

    await handle_email_skip(message, state)

    state.clear.assert_awaited_once()
    assert message.answer.await_count == 2
