# cantarella
# Don't Remove Credit
# Telegram Channel @cantarellabots

from pyrogram import Client, filters
from pyrogram.types import Message
from cantarella.auth import admin_filter
from database.db import db
from config import DB_URI

@Client.on_message(filters.command("ban") & admin_filter)
async def ban(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("**Usage:** `/ban user_id`")
    try:
        user_id = int(message.command[1])
        await db.ban_user(user_id)
        await message.reply_text(f"**User {user_id} Banned Successfully 🚫**")
    except:
        await message.reply_text("Error banning user.")

@Client.on_message(filters.command("unban") & admin_filter)
async def unban(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("**Usage:** `/unban user_id`")
    try:
        user_id = int(message.command[1])
        await db.unban_user(user_id)
        await message.reply_text(f"**User {user_id} Unbanned Successfully ✅**")
    except:
        await message.reply_text("Error unbanning user.")
# cantarella
# Don't Remove Credit
# Telegram Channel @cantarellabots

@Client.on_message(filters.command("set_dump") & admin_filter)
async def set_dump(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("**Usage:** `/set_dump user_id chat_id`")
    try:
        user_id = int(message.command[1])
        chat_id = int(message.command[2])
        await db.set_dump_chat(user_id, chat_id)
        await message.reply_text(f"**Dump chat set for user {user_id}.**")
    except:
        await message.reply_text("Error setting dump chat.")

@Client.on_message(filters.command("dblink") & admin_filter)
async def dblink(client: Client, message: Message):
    await message.reply_text(f"**DB URI:** `{DB_URI}`")

@Client.on_message(filters.command(["add_unsubscribe", "del_unsubscribe"]) & admin_filter)
async def manage_force_subscribe(client: Client, message: Message):
    await message.reply_text("Force Subscribe management feature is coming soon.")

# cantarella
# Don't Remove Credit
# Telegram Channel @cantarellabots


import asyncio
import os
import sys
from cantarella.start import batch_temp


@Client.on_message(filters.command("status") & admin_filter)
async def admin_status(client: Client, message: Message):
    total_users = await db.total_users_count()

    try:
        db_stats = await db.get_db_storage_stats()
        db_info = (
            f"Data: <code>{db_stats['data_size_mb']:.2f} MB</code>\n"
            f"Storage: <code>{db_stats['storage_size_mb']:.2f} MB</code>\n"
            f"Collections: <code>{db_stats['collections']}</code>"
        )
    except Exception as e:
        db_info = f"Unavailable: <code>{e}</code>"

    processing_users = sum(1 for in_progress in batch_temp.IS_BATCH.values() if in_progress is False)
    running_tasks = sum(1 for task in asyncio.all_tasks() if not task.done())

    try:
        load1, load5, load15 = os.getloadavg()
        load_info = f"<code>{load1:.2f}, {load5:.2f}, {load15:.2f}</code> (1m, 5m, 15m)"
    except Exception:
        load_info = "Not available"

    await message.reply_text(
        "<b>📊 Admin Bot Status</b>\n\n"
        f"<b>Total Users:</b> <code>{total_users}</code>\n"
        f"<b>Users in Active Task:</b> <code>{processing_users}</code>\n"
        f"<b>Running Async Tasks:</b> <code>{running_tasks}</code>\n"
        f"<b>System Load:</b> {load_info}\n\n"
        f"<b>MongoDB Usage</b>\n{db_info}",
        disable_web_page_preview=True
    )


@Client.on_message(filters.command("restart") & admin_filter)
async def admin_restart(client: Client, message: Message):
    # Admin-only hard restart: this stops all currently running save/batch tasks.
    for user_id in list(batch_temp.IS_BATCH.keys()):
        batch_temp.IS_BATCH[user_id] = True

    await message.reply_text(
        "<b>♻️ Restarting bot...</b>\n"
        "<i>Admin command received. All working tasks are being stopped now.</i>"
    )

    await asyncio.sleep(1)
    os.execl(sys.executable, sys.executable, *sys.argv)
