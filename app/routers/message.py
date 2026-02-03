from fastapi import APIRouter, Depends, status, HTTPException

from app.database import get_db
from app.models.chat import Chat
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/chats", tags=["messages"])

@router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(chat_id: int, msg_in: MessageCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Чат не найден")

    message = Message(
        chat_id=chat_id,
        text=msg_in.text
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message




