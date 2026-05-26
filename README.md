# HackatonMAy — Платформа олимпиад

Система для поиска и рекомендации школьных олимпиад, состоящая из Telegram-бота, веб-сервера, парсера и базы данных.

## Архитектура

| Компонент | Описание |
|-----------|----------|
| **db** | PostgreSQL — хранение пользователей и олимпиад |
| **bot** | Telegram-бот (aiogram) — регистрация пользователей (предмет, класс, регион) |
| **server** | HTTPS-сервер на C++ — REST API с AI-рекомендациями олимпиад |
| **parser** | Python-скрипт — загрузка олимпиад из CSV в БД |
| **ngrok** | Туннель для внешнего доступа к серверу |

## API (server)

- `POST /profile/{tg_id}` — данные пользователя
- `POST /api/olimps/{tg_id}` — список подходящих олимпиад (JSON с id)
- `POST /api/olimp:{id}/{tg_id}` — детали олимпиады + AI-объяснение релевантности

## Запуск

```bash
# 1. Настройте .env (BOT_TOKEN, POSTGRES_* и т.д.)
# 2. Запуск основных сервисов:
docker compose up -d

# 3. Запуск парсера (отдельный профиль):
docker compose --profile tools up parser
```

## Стек

- **Python** — aiogram, asyncpg, psycopg2
- **C++** — OpenSSL, libpq, raw sockets
- **PostgreSQL** — таблицы `users`, `events`
- **Docker Compose** — оркестрация
