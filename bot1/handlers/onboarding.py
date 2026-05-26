from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from keyboards.onboarding import (
    CONSENT_AGREE_CB,
    CONSENT_DECLINE_CB,
    email_skip_keyboard,
    main_menu_keyboard,
    open_webapp_keyboard,
    subject_keyboard,
)
from services.users import UserService, subject_code_to_label, subject_codes_to_labels
from states.onboarding import OnboardingStates
from texts import ru
from utils.validators import normalize_email

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
        reply_markup=subject_keyboard(),
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

    if not message.text.strip():
        await message.answer(ru.PROFILE_SUBJECTS_INVALID)
        return

    await state.update_data(subjects=message.text)
    await state.set_state(OnboardingStates.waiting_class)
    await message.answer(ru.PROFILE_CLASS_PROMPT, reply_markup=ReplyKeyboardRemove())


@router.message(OnboardingStates.waiting_class, F.text)
async def handle_class_input(message: Message, state: FSMContext) -> None:
    if message.text is None:
        return

    try:
        class_value = int(message.text.strip())
        if class_value <= 0:
            raise ValueError
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

    data = await state.get_data()
    try:
        await user_service.save_profile(
            message.from_user.id,
            subjects=str(data["subjects"]),
            class_value=str(data["class_value"]),
            region=message.text,
        )
    except KeyError:
        await state.clear()
        await message.answer(ru.UNKNOWN_COMMAND)
        return
    except ValueError:
        await message.answer(ru.PROFILE_REGION_INVALID)
        return

    await state.set_state(OnboardingStates.waiting_email)
    await message.answer(ru.PROFILE_SAVED)
    await message.answer(
        ru.EMAIL_PROMPT,
        reply_markup=email_skip_keyboard(),
    )


@router.message(OnboardingStates.waiting_email, F.text == ru.EMAIL_SKIP_BUTTON)
async def handle_email_skip(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        ru.EMAIL_SKIPPED,
        reply_markup=main_menu_keyboard(),
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
        reply_markup=main_menu_keyboard(),
    )
    await message.answer(
        ru.OPEN_WEBAPP_BUTTON,
        reply_markup=open_webapp_keyboard(),
    )


@router.message(F.text == ru.ADD_SUBJECT_BUTTON)
async def handle_add_subject_button(
    message: Message,
    state: FSMContext,
    user_service: UserService,
) -> None:
    if message.from_user is None:
        return

    profile = await user_service.get_profile(message.from_user.id)
    if (
        profile is None
        or profile.subjects is None
        or profile.class_ is None
        or profile.region is None
    ):
        await message.answer(ru.PROFILE_REQUIRED)
        return

    await state.set_state(OnboardingStates.adding_subject)
    await message.answer(ru.ADD_SUBJECT_PROMPT, reply_markup=subject_keyboard())


@router.message(OnboardingStates.adding_subject, F.text)
async def handle_additional_subject_input(
    message: Message,
    state: FSMContext,
    user_service: UserService,
) -> None:
    if message.from_user is None or message.text is None:
        return

    try:
        result = await user_service.add_subject(message.from_user.id, message.text)
    except ValueError:
        await message.answer(ru.PROFILE_SUBJECTS_INVALID)
        return

    await state.clear()
    subject_label = subject_code_to_label(result.code)
    if result.added:
        await message.answer(
            ru.ADD_SUBJECT_ADDED.format(
                subject=subject_label,
                subjects=subject_codes_to_labels(result.subjects),
            ),
            reply_markup=main_menu_keyboard(),
        )
        return

    await message.answer(
        ru.ADD_SUBJECT_EXISTS.format(subject=subject_label),
        reply_markup=main_menu_keyboard(),
    )


@router.message()
async def handle_unknown(message: Message) -> None:
    await message.answer(ru.UNKNOWN_COMMAND)
