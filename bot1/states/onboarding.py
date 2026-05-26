from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    waiting_consent = State()
    waiting_subjects = State()
    waiting_class = State()
    waiting_region = State()
    waiting_email = State()
    adding_subject = State()
