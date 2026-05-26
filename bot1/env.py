from os import getenv
TOKEN = getenv("TOKEN")
admin = int(getenv("TG_ADMIN_ID") or "0")

POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_DB = getenv("POSTGRES_DB")
