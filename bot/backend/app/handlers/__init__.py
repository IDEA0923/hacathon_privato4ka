from aiogram import Router

from . import onboarding, start


def build_root_router() -> Router:
    router = Router(name="root")
    router.include_router(start.router)
    router.include_router(onboarding.router)
    return router
