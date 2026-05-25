from os import getenv

POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_DB = getenv("POSTGRES_DB")
POSTGRES_HOST = getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = 5432

# Общие настройки парсинга
USER_AGENT = "(+contact: admin)"
REQUEST_TIMEOUT = 15.0
REQUEST_DELAY = 1.5  # секунд между запросами к одному источнику
