from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    title: str
    subjects: str
    class_: int = Field(alias="class")
    region: str
    event_date: date
    description: str | None = None
    link: str | None = None
