from .base import BaseSource, HttpClient
from .olimpiada_ru import OlimpiadaRu
from .rsr_olymp import RsrOlymp

ALL_SOURCES: list[type[BaseSource]] = [OlimpiadaRu, RsrOlymp]

__all__ = ["BaseSource", "HttpClient", "OlimpiadaRu", "RsrOlymp", "ALL_SOURCES"]
