from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import Settings
from app.handlers import build_root_router
from app.repositories.users import SQLiteUserRepository
from app.services.users import UserService


def build_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def build_dispatcher(user_service: UserService) -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher["user_service"] = user_service
    dispatcher.include_router(build_root_router())
    return dispatcher


def build_user_service(database_path: str = "bot.sqlite3") -> UserService:
    repository = SQLiteUserRepository(database_path)
    return UserService(repository=repository)
