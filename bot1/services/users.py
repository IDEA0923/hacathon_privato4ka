from dataclasses import dataclass
from datetime import datetime, timezone
import re

from dbs_div import pg
from models.user import User
from repositories.users import UserRepository

_SUBJECT_DELIMITERS_RE = re.compile(r"[,;+\n]+")
_REGION_CODES = {
    "moscow": 1,
    "primorsky": 2,
}
_SUBJECT_LABELS = {
    "mat": "Математика",
    "inf": "Информатика",
    "phy": "Физика",
    "che": "Химия",
    "bio": "Биология",
    "rus": "Русский язык",
    "lit": "Литература",
    "his": "История",
    "soc": "Обществознание",
    "eng": "Английский язык",
    "ast": "Астрономия",
    "geo": "География",
    "tec": "Технология",
}
_SUBJECT_ALIASES = {
    "mat": "mat",
    "math": "mat",
    "mathematics": "mat",
    "математика": "mat",
    "математик": "mat",
    "мат": "mat",
    "алгебра": "mat",
    "геометрия": "mat",
    "inf": "inf",
    "informatics": "inf",
    "computer science": "inf",
    "информатика": "inf",
    "информатик": "inf",
    "инф": "inf",
    "программирование": "inf",
    "phy": "phy",
    "physics": "phy",
    "физика": "phy",
    "физик": "phy",
    "физ": "phy",
    "che": "che",
    "chemistry": "che",
    "химия": "che",
    "хим": "che",
    "bio": "bio",
    "biology": "bio",
    "биология": "bio",
    "био": "bio",
    "rus": "rus",
    "russian": "rus",
    "русский": "rus",
    "русский язык": "rus",
    "lit": "lit",
    "literature": "lit",
    "литература": "lit",
    "his": "his",
    "history": "his",
    "история": "his",
    "soc": "soc",
    "social science": "soc",
    "обществознание": "soc",
    "право": "soc",
    "экономика": "soc",
    "eng": "eng",
    "english": "eng",
    "английский": "eng",
    "иностранный язык": "eng",
    "ast": "ast",
    "astronomy": "ast",
    "астрономия": "ast",
    "geo": "geo",
    "geography": "geo",
    "география": "geo",
    "tec": "tec",
    "technology": "tec",
    "технология": "tec",
    "инженерия": "tec",
}
_LEGACY_ONE_LETTER_CODES = {
    "m": "mat",
    "i": "inf",
    "p": "phy",
    "c": "che",
    "b": "bio",
    "r": "rus",
    "l": "lit",
    "h": "his",
    "s": "soc",
    "e": "eng",
    "a": "ast",
    "d": "geo",
    "t": "tec",
    "g": "mat",
}


@dataclass(frozen=True)
class AddSubjectResult:
    added: bool
    code: str
    subjects: str


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
        subjects: str,
        class_value: str | int,
        region: str,
    ) -> User:
        subjects_code = _build_subjects_code(subjects)
        class_number = _parse_class(class_value)
        region_code = _parse_region(region)

        user = await self._repository.get(tg_id)
        if user is None:
            user = User(tg_id=tg_id)
        user = user.model_copy(
            update={
                "subjects": subjects_code,
                "class_": class_number,
                "region": region_code,
            }
        )
        saved = await self._repository.upsert(user)
        if getattr(pg, "conn", None) is not None:
            await pg.save_user(tg_id, subjects_code, class_number, region_code)
        return saved

    async def get(self, tg_id: int) -> User | None:
        return await self._repository.get(tg_id)

    async def get_profile(self, tg_id: int) -> User | None:
        if getattr(pg, "conn", None) is not None:
            row = await pg.get_user(tg_id)
            if row is not None:
                user = await self._repository.get(tg_id) or User(tg_id=tg_id)
                user = user.model_copy(
                    update={
                        "subjects": row["subjects"],
                        "class_": row["class"],
                        "region": row["region"],
                    }
                )
                return await self._repository.upsert(user)
        return await self._repository.get(tg_id)

    async def add_subject(self, tg_id: int, subject: str) -> AddSubjectResult:
        code = _normalize_subject_to_code(subject)
        user = await self.get_profile(tg_id)
        if user is None or user.class_ is None or user.region is None:
            raise ValueError("Profile not found")

        current_subjects = user.subjects or ""
        updated_subjects, added = append_subject_code(current_subjects, code)
        if added:
            user = user.model_copy(update={"subjects": updated_subjects})
            await self._repository.upsert(user)
            if getattr(pg, "conn", None) is not None:
                await pg.update_user_subjects(tg_id, updated_subjects)

        return AddSubjectResult(
            added=added,
            code=code,
            subjects=updated_subjects,
        )


def _build_subjects_code(subjects: str) -> str:
    codes: list[str] = []
    seen: set[str] = set()

    for code in split_subject_codes(subjects):
        if not code or code in seen:
            continue
        seen.add(code)
        codes.append(code)

    if not codes:
        raise ValueError("At least one subject is required")
    return "".join(codes)


def split_subject_codes(subjects: str | None) -> list[str]:
    if not subjects:
        return []

    raw = subjects.strip().lower()
    if not raw:
        return []

    if _SUBJECT_DELIMITERS_RE.search(raw):
        return [
            _normalize_subject_to_code(part)
            for part in _SUBJECT_DELIMITERS_RE.split(raw)
            if part.strip()
        ]

    compact = raw.replace(" ", "")
    if (
        compact not in _SUBJECT_LABELS
        and compact not in _SUBJECT_ALIASES
        and all(ch in _LEGACY_ONE_LETTER_CODES for ch in compact)
    ):
        return [_LEGACY_ONE_LETTER_CODES[ch] for ch in compact]

    if len(compact) % 3 == 0:
        codes: list[str] = []
        for i in range(0, len(compact), 3):
            chunk = compact[i : i + 3]
            if chunk:
                codes.append(_SUBJECT_ALIASES.get(chunk, chunk))
        return codes

    return [_normalize_subject_to_code(raw)]


def append_subject_code(current_subjects: str | None, code: str) -> tuple[str, bool]:
    current_codes = _build_subjects_code(current_subjects or "") if current_subjects else ""
    codes = split_subject_codes(current_codes)
    if code in codes:
        return "".join(codes), False
    codes.append(code)
    return "".join(codes), True


def subject_code_to_label(code: str) -> str:
    return _SUBJECT_LABELS.get(code, code)


def subject_codes_to_labels(subjects: str | None) -> str:
    codes = split_subject_codes(subjects)
    if not codes:
        return "не выбраны"
    return ", ".join(subject_code_to_label(code) for code in codes)


def _normalize_subject_to_code(subject: str) -> str:
    normalized = re.sub(r"\s+", " ", subject.strip().lower())
    if not normalized:
        raise ValueError("At least one subject is required")

    if normalized in _SUBJECT_ALIASES:
        return _SUBJECT_ALIASES[normalized]

    for alias, code in _SUBJECT_ALIASES.items():
        if len(alias) > 3 and alias in normalized:
            return code

    compact = normalized.replace(" ", "")
    if len(compact) == 3:
        return compact
    if len(compact) > 3:
        return compact[:3]
    raise ValueError("Subject code must contain at least 3 characters")


def _parse_class(value: str | int) -> int:
    if isinstance(value, bool):
        raise ValueError("Class must be an integer")
    if isinstance(value, int):
        class_number = value
    else:
        class_number = int(value.strip())
    if class_number <= 0:
        raise ValueError("Class must be positive")
    return class_number


def _parse_region(region: str) -> int:
    try:
        return _REGION_CODES[region.strip().lower()]
    except KeyError:
        raise ValueError("Unknown region") from None
