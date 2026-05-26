from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tg_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    consent_at: datetime | None = None
    subjects: str | None = None
    class_: int | None = Field(default=None, alias="class")
    region: int | None = None
