from pyrogram import filters

from config import ADMINS


ADMIN_IDS = set(ADMINS)


def is_admin_user(user_id: int) -> bool:
    return bool(user_id in ADMIN_IDS)


async def _admin_filter(_, __, message):
    user = getattr(message, "from_user", None)
    return bool(user and is_admin_user(user.id))


admin_filter = filters.create(_admin_filter)
