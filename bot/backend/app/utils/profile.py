from collections.abc import Iterable
import re


_SUBJECT_DELIMITERS_RE = re.compile(r"[,;+\n]+")


def normalize_short_code(value: str) -> str:
    normalized = value.strip().lower()
    return normalized[:3]


def build_subjects_code(subjects: str | Iterable[str]) -> str:
    parts = _split_subject_values(subjects)
    codes: list[str] = []
    seen: set[str] = set()

    for part in parts:
        code = normalize_short_code(part)
        if not code or code in seen:
            continue
        seen.add(code)
        codes.append(code)

    if not codes:
        raise ValueError("At least one subject is required")
    return "".join(codes)


def parse_class(value: str | int) -> int:
    if isinstance(value, bool):
        raise ValueError("Class must be an integer")
    if isinstance(value, int):
        class_number = value
    else:
        raw = value.strip()
        if not raw:
            raise ValueError("Class must not be empty")
        class_number = int(raw)

    if class_number <= 0:
        raise ValueError("Class must be positive")
    return class_number


def normalize_region_code(region: str) -> str:
    code = normalize_short_code(region)
    if not code:
        raise ValueError("Region must not be empty")
    return code


def split_compact_codes(value: str | None) -> set[str]:
    if value is None:
        return set()

    text = value.strip().lower()
    if not text:
        return set()

    if _SUBJECT_DELIMITERS_RE.search(text):
        return {
            normalize_short_code(part)
            for part in _SUBJECT_DELIMITERS_RE.split(text)
            if normalize_short_code(part)
        }

    if len(text) <= 3 or len(text) % 3 != 0:
        return {text[:3]}

    return {
        text[index : index + 3]
        for index in range(0, len(text), 3)
        if len(text[index : index + 3]) == 3
    }


def subjects_match(event_subjects: str | None, user_subjects: str | None) -> bool:
    return bool(split_compact_codes(event_subjects) & split_compact_codes(user_subjects))


def _split_subject_values(subjects: str | Iterable[str]) -> list[str]:
    if isinstance(subjects, str):
        return _SUBJECT_DELIMITERS_RE.split(subjects)

    parts: list[str] = []
    for subject in subjects:
        parts.extend(_SUBJECT_DELIMITERS_RE.split(subject))
    return parts
