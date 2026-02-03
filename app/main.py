from fastapi import FastAPI
from app.routers.message import router as message_router
from app.routers.chat import router as chat_router

app = FastAPI()

app.include_router(message_router)
app.include_router(chat_router)

@app.get("/")
def welcome():
    return "Welcome. API is running!"

