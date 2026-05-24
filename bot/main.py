import asyncio
import logging

from bot import build_bot, build_dispatcher, build_user_service
from config import get_settings


async def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    settings = get_settings()
    user_service = build_user_service()
    bot = build_bot(settings)
    dispatcher = build_dispatcher(user_service)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
