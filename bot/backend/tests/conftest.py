import os
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("BOT_TOKEN", "test:token")

from app.repositories.users import InMemoryUserRepository  # noqa: E402
from app.services.users import UserService  # noqa: E402


@pytest.fixture
def repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def user_service(repository: InMemoryUserRepository) -> UserService:
    return UserService(repository=repository)
