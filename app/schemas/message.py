from typing import List

from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime


class MessageCreate(BaseModel):
    text: str

    @field_validator("text", mode="before")
    @classmethod
    def clean_and_validate_text(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Текст сообщения не может быть пустым после удаления пробелов")
        if not (1 <= len(cleaned) <= 5000):
            raise ValueError("Длина сообщения должна быть от 1 до 5000 символов")
        return cleaned


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

