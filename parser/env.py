import os

# Маппим старые названия из .env на те, что используются в коде БД
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

# Общие настройки парсинга
USER_AGENT = "(+contact: admin)"
REQUEST_TIMEOUT = 15.0
REQUEST_DELAY = 1.5  # секунд между запросами к одному источнику
