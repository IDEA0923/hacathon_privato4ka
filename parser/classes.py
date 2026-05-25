"""Извлечение диапазона классов из текста.

Возвращает (class_start, class_end). Если не нашлось — (0, 11).
"""

import re

# "5-11 классы", "5–11 кл.", "с 7 по 11 класс", "8 класс", "10, 11 классы"
_RANGE_RE = re.compile(
    r"(\d{1,2})\s*[-–—]\s*(\d{1,2})\s*кл",
    re.IGNORECASE,
)
_RANGE_RE2 = re.compile(
    r"с\s*(\d{1,2})\s*по\s*(\d{1,2})\s*класс",
    re.IGNORECASE,
)
_SINGLE_RE = re.compile(
    r"(?<!\d)(\d{1,2})\s*класс",
    re.IGNORECASE,
)


def detect_classes(text: str) -> tuple[int, int]:
    if not text:
        return (0, 11)

    m = _RANGE_RE.search(text) or _RANGE_RE2.search(text)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        a, b = sorted((a, b))
        return (_clamp(a), _clamp(b))

    nums = [int(x.group(1)) for x in _SINGLE_RE.finditer(text)]
    nums = [n for n in nums if 1 <= n <= 11]
    if nums:
        return (_clamp(min(nums)), _clamp(max(nums)))

    return (0, 11)


def _clamp(n: int) -> int:
    if n < 0:
        return 0
    if n > 11:
        return 11
    return n
