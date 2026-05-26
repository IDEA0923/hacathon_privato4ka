from os import getenv

TOKEN = getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("BOT TOKEN not set! Set TOKEN environment variable.")

admin_raw = getenv("TG_ADMIN_ID")
if not admin_raw:
    raise RuntimeError("TG_ADMIN_ID not set! Set TG_ADMIN_ID environment variable.")
admin = int(admin_raw)

POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_DB = getenv("POSTGRES_DB")
