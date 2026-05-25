from collections.abc import Iterable
from datetime import date
from datetime import datetime, timezone

from app.models.event import Event
from app.models.user import User
from app.repositories.users import UserRepository
from app.utils.profile import (
    build_subjects_code,
    normalize_region_code,
    parse_class,
)


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

    async def save_profile(
        self,
        tg_id: int,
        *,
        subjects: str | Iterable[str],
        class_value: str | int,
        region: str,
    ) -> User:
        subjects_code = build_subjects_code(subjects)
        class_number = parse_class(class_value)
        region_code = normalize_region_code(region)
        return await self._repository.save_profile(
            tg_id,
            subjects=subjects_code,
            class_value=class_number,
            region=region_code,
        )

    async def find_matching_events(
        self,
        tg_id: int,
        *,
        today: date | None = None,
    ) -> list[Event]:
        return await self._repository.find_matching_events(tg_id, today=today)

    async def get(self, tg_id: int) -> User | None:
        return await self._repository.get(tg_id)
