from typing import Protocol

from models.user import User


class UserRepository(Protocol):
    async def get(self, tg_id: int) -> User | None: ...
    async def upsert(self, user: User) -> User: ...


class InMemoryUserRepository:
    """In-memory заглушка вместо реальной БД.

    Подходит для первого пользовательского сценария. Данные теряются
    при рестарте процесса — реальный репозиторий подключим позже.
    """

    def __init__(self) -> None:
        self._items: dict[int, User] = {}

    async def get(self, tg_id: int) -> User | None:
        return self._items.get(tg_id)

    async def upsert(self, user: User) -> User:
        self._items[user.tg_id] = user
        return user
