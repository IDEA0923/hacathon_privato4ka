from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from keyboards.onboarding import (
    CONSENT_AGREE_CB,
    CONSENT_DECLINE_CB,
    email_skip_keyboard,
    open_webapp_keyboard,
)
from services.users import UserService
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
    await state.set_state(OnboardingStates.waiting_email)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        ru.CONSENT_ACCEPTED,
        reply_markup=email_skip_keyboard(),
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
