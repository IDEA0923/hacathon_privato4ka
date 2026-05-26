import asyncio
from contextlib import suppress
import logging

from bot import build_bot, build_dispatcher, build_user_service
from config import get_settings
from dbs_div import pg
from services.notifications import notification_worker


async def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    settings = get_settings()
    await pg.connect()
    await pg.ensure_schema()
    user_service = build_user_service()
    bot = build_bot(settings)
    dispatcher = build_dispatcher(user_service)
    notifications_task = asyncio.create_task(notification_worker(bot))

    try:
        await dispatcher.start_polling(bot)
    finally:
        notifications_task.cancel()
        with suppress(asyncio.CancelledError):
            await notifications_task
        await pg.close()
        await bot.session.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
