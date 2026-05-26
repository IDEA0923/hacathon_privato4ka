from os import getenv

TOKEN = getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("BOT TOKEN not set! Set TOKEN environment variable.")

admin_raw = getenv("TG_ADMIN_ID")
if not admin_raw:
    raise RuntimeError("TG_ADMIN_ID not set! Set TG_ADMIN_ID environment variable.")
admin = int(admin_raw)

POSTGRES_USER = getenv("POSTGRES_USER")
if not POSTGRES_USER:
    raise RuntimeError("POSTGRES_USER not set! Set POSTGRES_USER environment variable.")

POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
if not POSTGRES_PASSWORD:
    raise RuntimeError("POSTGRES_PASSWORD not set! Set POSTGRES_PASSWORD environment variable.")

POSTGRES_DB = getenv("POSTGRES_DB")
if not POSTGRES_DB:
    raise RuntimeError("POSTGRES_DB not set! Set POSTGRES_DB environment variable.")
