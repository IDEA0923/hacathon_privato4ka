import os
from dotenv import load_dotenv

load_dotenv()

# Маппим старые названия из .env на те, что используются в коде БД
POSTGRES_USER = os.getenv("postgress_login", "admin")
POSTGRES_PASSWORD = os.getenv("postgress_password", "X1imSH2iFhiqgxGBtx8M")
POSTGRES_DB = os.getenv("POSTGRES_DB", "datab")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

# Общие настройки парсинга
USER_AGENT = "(+contact: admin)"
REQUEST_TIMEOUT = 15.0
REQUEST_DELAY = 1.5  # секунд между запросами к одному источнику
