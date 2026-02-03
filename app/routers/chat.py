from fastapi import APIRouter, Depends, status, HTTPException, Query


from app.database import get_db
from app.models.chat import Chat
from app.models.message import Message
from app.schemas.chat import ChatCreate, ChatResponse, ChatDetailResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(chat: ChatCreate, db: AsyncSession = Depends(get_db)):
    new_chat = Chat(title=chat.title)
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)

    return new_chat

@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat_detail(chat_id: int, db: AsyncSession = Depends(get_db), limit: int = Query(20, ge=1, le=100)):
    # поиск чата
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Чат не найден")

    # последние сообщения(limit) по убыванию
    msg_result = await db.execute(select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.desc()).limit(limit))
    messages = msg_result.scalars().all()

    # ответ
    return ChatDetailResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        messages=messages
    )


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(chat_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Чат не найден")

    await db.delete(chat)
    await db.commit()
    return None # 204 вернётся автоматически



