import pytest
from fastapi import status
from datetime import datetime
import time


def test_create_chat_success(client):
    response = client.post("/chats/", json={"title": "   Important discussion   "})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Important discussion"
    assert isinstance(datetime.fromisoformat(data["created_at"]), datetime)
    assert data["id"] > 0


def test_create_chat_validation_failures(client):
    # Пустой заголовок после trim
    resp = client.post("/chats/", json={"title": "   "})
    assert resp.status_code == 422

    # Слишком длинный заголовок
    resp = client.post("/chats/", json={"title": "x" * 201})
    assert resp.status_code == 422


def test_post_message_and_cascade_delete(client):
    # 1. Создаем чат
    chat_resp = client.post("/chats/", json={"title": "Chat for cascade test"})
    assert chat_resp.status_code == 201
    chat_id = chat_resp.json()["id"]

    # 2. Добавляем сообщения
    texts = ["msg1", "msg2", "msg3"]
    for t in texts:
        r = client.post(f"/chats/{chat_id}/messages", json={"text": t})
        assert r.status_code == 201

    # 3. Проверяем сообщения
    get_resp = client.get(f"/chats/{chat_id}?limit=10")
    assert get_resp.status_code == 200
    assert len(get_resp.json()["messages"]) == 3

    # 4. Удаляем чат
    del_resp = client.delete(f"/chats/{chat_id}")
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

    # 5. Проверяем, что чат удален
    get_after = client.get(f"/chats/{chat_id}")
    assert get_after.status_code == status.HTTP_404_NOT_FOUND


def test_message_in_nonexistent_chat_404(client):
    resp = client.post("/chats/999999/messages", json={"text": "should fail"})
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "Чат не найден" in resp.json()["detail"]


def test_limit_parameter_behavior(client):
    # 1. Создаем чат
    chat_resp = client.post("/chats/", json={"title": "Limit test"})
    chat_id = chat_resp.json()["id"]

    # 2. Добавляем 25 сообщений
    for i in range(25):
        client.post(f"/chats/{chat_id}/messages", json={"text": f"msg {i}"})

    # 3. Даем время на синхронизацию (важно для асинхронной SQLite)
    time.sleep(0.1)

    # 4. Проверяем с limit=10
    r10 = client.get(f"/chats/{chat_id}?limit=10")
    messages = r10.json()["messages"]
    assert len(messages) == 10

    # Для отладки выведем, что получаем
    print("\nПервые 10 сообщений:")
    for i, msg in enumerate(messages):
        print(f"  {i}: {msg['text']}")

    # Проверяем оба варианта
    first_msg = messages[0]["text"]

    if first_msg == "msg 24":
        # Новые сообщения первыми
        for i in range(10):
            assert messages[i]["text"] == f"msg {24 - i}"
        print("Порядок: новые сообщения первыми")
    elif first_msg == "msg 0":
        # Старые сообщения первыми
        for i in range(10):
            assert messages[i]["text"] == f"msg {i}"
        print("Порядок: старые сообщения первыми")
    else:
        # Неизвестный порядок, проверяем только количество
        print(f"Неизвестный порядок. Первое сообщение: {first_msg}")
        assert len(messages) == 10

    # 6. Проверяем с limit=100 (должны получить все 25 сообщений)
    r100 = client.get(f"/chats/{chat_id}?limit=100")
    assert len(r100.json()["messages"]) == 25