# Backend — Telegram-бот (онбординг)

Telegram-бот на aiogram 3 для первого пользовательского сценария:
приветствие → согласие на использование базовых данных Telegram →
ввод email (можно пропустить) → подтверждение и кнопка-заглушка перехода
в веб-приложение.

> Данные профиля пользователя хранятся в SQLite через `SQLiteUserRepository`.
> По умолчанию используется файл `bot.sqlite3`; путь можно переопределить
> переменной окружения `DATABASE_PATH`.

## Требования

- Python 3.12+
- Telegram Bot Token от [@BotFather](https://t.me/BotFather)

## Установка

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Конфигурация

```powershell
Copy-Item .env.example .env
```

В файле `.env` укажите ваш `BOT_TOKEN`.

## Запуск бота

```powershell
python -m app.main
```

После запуска отправьте боту `/start` в Telegram.

## Запуск тестов

```powershell
pytest
```

## Структура

```
app/
  config.py           # настройки (pydantic-settings)
  bot.py              # сборка Bot/Dispatcher и DI
  main.py             # точка входа (long polling)
  handlers/           # /start и FSM онбординга
  keyboards/          # inline/reply клавиатуры
  states/             # состояния FSM
  texts/ru.py         # тексты интерфейса (RU)
  services/users.py   # бизнес-логика по пользователю
  repositories/users.py  # SQLite/InMemory-репозитории
  database/queries.py # запросы к SQLite
  models/user.py      # pydantic-модель User
  models/event.py     # pydantic-модель Event
  utils/validators.py # валидация email
tests/                # pytest + pytest-asyncio
migrations/           # SQL-схемы SQLite
```

## Сценарий

1. `/start` — приветствие и inline-кнопки «Согласен / Отказаться».
2. «Согласен» — фиксируем `consent_at`, просим предметы, класс и регион.
3. Профиль сохраняется в БД: `tg_id`, `subjects`, `class`, `region`.
4. Бот показывает подходящие мероприятия на ближайший месяц, если они есть.
5. Email — валидируется и сохраняется; «Пропустить» — пропускаем шаг.
6. В конце показывается кнопка «Открыть веб-приложение» (заглушка).
