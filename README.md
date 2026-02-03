# Chat API

Современное REST API для чатов и сообщений с валидацией, каскадным удалением и тестами.

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/JolyRed/Test_task_chat_api/actions)

## О проекте

Простое, но полноценное API для работы с чатами и сообщениями:

- Создание чатов
- Отправка сообщений в чат
- Получение чата + последних N сообщений (сортировка по дате DESC)
- Каскадное удаление чата и всех его сообщений
- Полная валидация входных данных (Pydantic v2)
- Обработка ошибок (404 при несуществующем чате)
- Асинхронный стек (SQLAlchemy 2.0 + asyncpg)
- Тесты на SQLite в памяти
- Docker + docker-compose для запуска

## Функционал API

| Метод       | Эндпоинт                          | Описание                                      | Тело запроса          |
|-------------|-----------------------------------|-----------------------------------------------|-----------------------|
| POST        | `/chats/`                         | Создать чат                                   | `{ "title": str }`    |
| POST        | `/chats/{chat_id}/messages`       | Отправить сообщение в чат                     | `{ "text": str }`     |
| GET         | `/chats/{chat_id}?limit=20`       | Получить чат + последние сообщения (до 100)   | —                     |
| DELETE      | `/chats/{chat_id}`                | Удалить чат (каскадно удаляются сообщения)    | —                     |

**Валидация:**
- title: 1–200 символов, пробелы по краям обрезаются
- text: 1–5000 символов, пробелы по краям обрезаются
- 404 при попытке отправить сообщение в несуществующий чат

## Технологии

- **Backend** — FastAPI
- **База данных** — PostgreSQL + SQLAlchemy 2.0 (async)
- **ORM** — SQLAlchemy 2.0 + asyncpg
- **Валидация** — Pydantic v2
- **Миграции** — Alembic
- **Тесты** — pytest + pytest-asyncio (SQLite :memory:)
- **Контейнеризация** — Docker + docker-compose
- **Зависимости** — управление через uv

## Быстрый запуск

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/JolyRed/Test_task_chat_api.git
cd Test_task_chat_api

# 2. Создайте .env (или используйте .env.example)
cp .env.example .env

# 3. Запустите
docker compose up --build
```

## Тесты
Для запуска тестов внутри запущенного контейнера необходимо:
```bash
docker compose run --rm api bash
pytest tests/ -v  
```

Если хотите запустить отдельно, то():
```bash
# 1. Создайте виртуальное окружение (если ещё нет)
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# или на Windows: .venv\Scripts\activate

# 2. Установите зависимости для тестов
pip install pytest pytest-asyncio httpx fastapi sqlalchemy[asyncio] asyncpg pydantic-settings

# 3. Запустите
pytest tests/ -v
```
Или если используете uv(рекомендовано):
```bash
# 1. Перейдите в корень проекта
cd Test_task_chat_api

# 2. Установите зависимости для тестов (если их ещё нет)
uv sync --dev

# 3. Запустите все тесты
uv run pytest tests/ -v
```
