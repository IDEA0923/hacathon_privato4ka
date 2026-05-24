from datetime import datetime, timezone

from models.user import User
from repositories.users import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def get_or_create(
        self,
        tg_id: int,
        *,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        existing = await self._repository.get(tg_id)
        if existing is not None:
            updated = existing.model_copy(
                update={
                    "username": username if username is not None else existing.username,
                    "first_name": first_name if first_name is not None else existing.first_name,
                    "last_name": last_name if last_name is not None else existing.last_name,
                }
            )
            return await self._repository.upsert(updated)

        user = User(
            tg_id=tg_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        return await self._repository.upsert(user)

    async def set_consent(self, tg_id: int) -> User:
        user = await self._repository.get(tg_id)
        if user is None:
            user = User(tg_id=tg_id)
        user = user.model_copy(update={"consent_at": datetime.now(timezone.utc)})
        return await self._repository.upsert(user)

    async def set_email(self, tg_id: int, email: str) -> User:
        user = await self._repository.get(tg_id)
        if user is None:
            raise ValueError(f"User {tg_id} not found")
        user = user.model_copy(update={"email": email})
        return await self._repository.upsert(user)

    async def get(self, tg_id: int) -> User | None:
        return await self._repository.get(tg_id)
