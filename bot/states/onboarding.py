from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    waiting_consent = State()
    waiting_email = State()
