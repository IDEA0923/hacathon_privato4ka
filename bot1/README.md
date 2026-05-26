# Backend — Telegram-бот (онбординг)

Telegram-бот на aiogram 3 для первого пользовательского сценария:
приветствие → согласие на использование базовых данных Telegram →
ввод email (можно пропустить) → подтверждение и кнопка-заглушка перехода
в веб-приложение.

> На этом этапе данные хранятся в памяти процесса
> (`InMemoryUserRepository`). При рестарте бота они теряются.
> Реальная БД будет подключена позже без изменения сервиса/хендлеров.

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
  repositories/users.py  # InMemory-репозиторий (заглушка БД)
  models/user.py      # pydantic-модель User
  utils/validators.py # валидация email
tests/                # pytest + pytest-asyncio
```

## Сценарий

1. `/start` — приветствие и inline-кнопки «Согласен / Отказаться».
2. «Согласен» — фиксируем `consent_at`, просим email или «Пропустить».
3. Email — валидируется и сохраняется; «Пропустить» — пропускаем шаг.
4. В конце показывается кнопка «Открыть веб-приложение» (заглушка).
