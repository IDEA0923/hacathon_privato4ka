from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from app.keyboards.onboarding import (
    CONSENT_AGREE_CB,
    CONSENT_DECLINE_CB,
    email_skip_keyboard,
    open_webapp_keyboard,
)
from app.models.event import Event
from app.services.users import UserService
from app.states.onboarding import OnboardingStates
from app.texts import ru
from app.utils.profile import build_subjects_code, normalize_region_code, parse_class
from app.utils.validators import normalize_email

router = Router(name="onboarding")


@router.callback_query(
    OnboardingStates.waiting_consent,
    F.data == CONSENT_AGREE_CB,
)
async def handle_consent_agree(
    callback: CallbackQuery,
    state: FSMContext,
    user_service: UserService,
) -> None:
    if callback.from_user is None or callback.message is None:
        await callback.answer()
        return

    await user_service.set_consent(callback.from_user.id)
    await state.set_state(OnboardingStates.waiting_subjects)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        ru.PROFILE_SUBJECTS_PROMPT,
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer()


@router.callback_query(
    OnboardingStates.waiting_consent,
    F.data == CONSENT_DECLINE_CB,
)
async def handle_consent_decline(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if callback.message is None:
        await callback.answer()
        return

    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(ru.CONSENT_DECLINED)
    await callback.answer()


@router.message(OnboardingStates.waiting_subjects, F.text)
async def handle_subjects_input(message: Message, state: FSMContext) -> None:
    if message.text is None:
        return

    try:
        build_subjects_code(message.text)
    except ValueError:
        await message.answer(ru.PROFILE_SUBJECTS_INVALID)
        return

    await state.update_data(subjects=message.text)
    await state.set_state(OnboardingStates.waiting_class)
    await message.answer(ru.PROFILE_CLASS_PROMPT)


@router.message(OnboardingStates.waiting_class, F.text)
async def handle_class_input(message: Message, state: FSMContext) -> None:
    if message.text is None:
        return

    try:
        parse_class(message.text)
    except ValueError:
        await message.answer(ru.PROFILE_CLASS_INVALID)
        return

    await state.update_data(class_value=message.text)
    await state.set_state(OnboardingStates.waiting_region)
    await message.answer(ru.PROFILE_REGION_PROMPT)


@router.message(OnboardingStates.waiting_region, F.text)
async def handle_region_input(
    message: Message,
    state: FSMContext,
    user_service: UserService,
) -> None:
    if message.from_user is None or message.text is None:
        return

    try:
        normalize_region_code(message.text)
    except ValueError:
        await message.answer(ru.PROFILE_REGION_INVALID)
        return

    data = await state.get_data()
    try:
        await user_service.save_profile(
            message.from_user.id,
            subjects=str(data["subjects"]),
            class_value=str(data["class_value"]),
            region=message.text,
        )
    except (KeyError, ValueError):
        await state.clear()
        await message.answer(ru.UNKNOWN_COMMAND)
        return

    events = await user_service.find_matching_events(message.from_user.id)
    await state.set_state(OnboardingStates.waiting_email)
    await message.answer(f"{ru.PROFILE_SAVED}\n\n{_format_events_message(events)}")
    await message.answer(
        ru.EMAIL_PROMPT,
        reply_markup=email_skip_keyboard(),
    )


@router.message(OnboardingStates.waiting_email, F.text == ru.EMAIL_SKIP_BUTTON)
async def handle_email_skip(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        ru.EMAIL_SKIPPED,
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        ru.OPEN_WEBAPP_BUTTON,
        reply_markup=open_webapp_keyboard(),
    )


@router.message(OnboardingStates.waiting_email, F.text)
async def handle_email_input(
    message: Message,
    state: FSMContext,
    user_service: UserService,
) -> None:
    if message.from_user is None or message.text is None:
        return

    try:
        email = normalize_email(message.text.strip())
    except ValueError:
        await message.answer(ru.EMAIL_INVALID)
        return

    await user_service.set_email(message.from_user.id, email)
    await state.clear()
    await message.answer(
        ru.EMAIL_SAVED.format(email=email),
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        ru.OPEN_WEBAPP_BUTTON,
        reply_markup=open_webapp_keyboard(),
    )


@router.message()
async def handle_unknown(message: Message) -> None:
    await message.answer(ru.UNKNOWN_COMMAND)


def _format_events_message(events: list[Event]) -> str:
    if not events:
        return ru.MATCHING_EVENTS_EMPTY

    lines = [ru.MATCHING_EVENTS_TITLE]
    for event in events:
        line = f"- {event.event_date:%d.%m.%Y}: {escape(event.title)}"
        if event.description:
            line = f"{line}\n  {escape(event.description)}"
        if event.link:
            line = f"{line}\n  {escape(event.link)}"
        lines.append(line)
    return "\n".join(lines)
