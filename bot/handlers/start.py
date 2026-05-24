from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.onboarding import consent_keyboard
from services.users import UserService
from states.onboarding import OnboardingStates
from texts import ru

router = Router(name="start")


@router.message(CommandStart())
async def handle_start(
    message: Message,
    state: FSMContext,
    user_service: UserService,
) -> None:
    tg_user = message.from_user
    if tg_user is None:
        return

    await user_service.get_or_create(
        tg_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
    )

    display_name = tg_user.first_name or tg_user.username or "друг"
    await state.set_state(OnboardingStates.waiting_consent)
    await message.answer(
        ru.WELCOME.format(name=display_name),
        reply_markup=consent_keyboard(),
    )
