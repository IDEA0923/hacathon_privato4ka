from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    tg_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    consent_at: datetime | None = None
