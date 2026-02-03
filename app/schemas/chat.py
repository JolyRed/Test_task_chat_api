from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import List
from app.schemas.message import MessageResponse


class ChatCreate(BaseModel):
    title: str

    @field_validator("title", mode="before")
    @classmethod
    def clean_and_validate_title(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Заголовок не может быть пустым после удаления пробелов")
        if not (1 <= len(cleaned) <= 200):
            raise ValueError("Длина заголовка должна быть от 1 до 200 символов")
        return cleaned


class ChatResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatDetailResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: List[MessageResponse]

    model_config = ConfigDict(from_attributes=True)
