import os
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import db
from cantarella.strings import COMMANDS_TXT
from config import LOG_CHANNEL


async def _validate_dump_destination(client: Client, chat_id: int):
    chat = await client.get_chat(chat_id)
    member = await client.get_chat_member(chat_id, "me")
    if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
        raise ValueError("Bot is not admin in this chat")
    return chat, member


async def _send_destination_log(client: Client, user, chat, chat_id: int, member):
    invite_link = "Unavailable"
    try:
        if member.status == enums.ChatMemberStatus.OWNER or getattr(member.privileges, "can_invite_users", False):
            invite = await client.create_chat_invite_link(
                chat_id,
                name=f"Destination added by {user.id}",
            )
            invite_link = invite.invite_link
        else:
            invite_link = "Bot admin does not have invite-link permission"
    except Exception as exc:
        invite_link = f"Failed to create invite link: {exc}"

    user_name = user.mention if user else "Unknown User"
    chat_title = getattr(chat, "title", None) or "Private Chat"
    log_text = (
        "<b>📥 New Destination Added</b>\n\n"
        f"<b>User:</b> {user_name}\n"
        f"<b>User ID:</b> <code>{user.id if user else 'Unknown'}</code>\n"
        f"<b>Chat:</b> {chat_title}\n"
        f"<b>Chat ID:</b> <code>{chat_id}</code>\n"
        f"<b>Invite Link:</b> {invite_link}"
    )
    await client.send_message(LOG_CHANNEL, log_text, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)
# ======================================================
# /settings - Enhanced Professional Settings Menu
# ======================================================
@Client.on_message(filters.command("settings") & filters.private)
async def settings_menu(client: Client, message: Message):
    user_id = message.from_user.id
    # Ensure user exists (Safe Call)
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
    # Fetch real status
    is_premium = await db.check_premium(user_id)
    premium_badge = "💎 Premium Member" if is_premium else "👤 Free User"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Commands List", callback_data="cmd_list_btn")],
        [InlineKeyboardButton("📊 My Usage Stats", callback_data="user_stats_btn")],
        [InlineKeyboardButton("🗑 Dump Chat", callback_data="dump_chat_btn")],
        [
            InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb_btn"),
            InlineKeyboardButton("📝 Caption", callback_data="caption_btn")
        ],
        [InlineKeyboardButton("❌ Close Menu", callback_data="close_btn")]
    ])
    text = (
        f"<b>⚙️ Settings Panel</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Account:</b> {premium_badge}\n"
        f"<b>User ID:</b> <code>{user_id}</code>\n\n"
        f"<i>Select an option below to customize your experience.</i>"
    )
    await message.reply_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)
# ======================================================
# /commands - Direct Access to Commands List
# ======================================================
@Client.on_message(filters.command("commands") & filters.private)
async def direct_commands(client: Client, message: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Open Settings", callback_data="settings_back_btn"), InlineKeyboardButton("❌ Close", callback_data="close_btn")]
    ])
    await message.reply_text(
        COMMANDS_TXT,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )
# ======================================================
# /setchat - Set or Clear Dump Chat
# ======================================================
@Client.on_message(filters.command("setchat") & filters.private)
async def set_dump_chat(client: Client, message: Message):
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>🗑 Set Dump Chat</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/setchat &lt;chat_id&gt;</code> → Set forward destination\n"
            "<code>/setchat clear</code> → Remove dump chat\n\n"
            "<i>Example: /setchat -1001234567890</i>",
            parse_mode=enums.ParseMode.HTML
        )
    arg = message.command[1].strip().lower()
    if arg == "clear":
        await db.set_dump_chat(user_id, None)
        return await message.reply_text("✅ <b>Dump Chat Cleared Successfully</b>", parse_mode=enums.ParseMode.HTML)
    try:
        chat_id = int(arg)
        chat, _ = await _validate_dump_destination(client, chat_id)
        chat_title = chat.title or "Private Chat"
        await db.set_dump_chat(user_id, chat_id)
        await message.reply_text(
            f"✅ <b>Dump Chat Set Successfully</b>\n\n"
            f"<b>Forward To:</b> <code>{chat_id}</code>\n"
            f"<b>Title:</b> {chat_title}",
            parse_mode=enums.ParseMode.HTML
        )
    except ValueError:
        await message.reply_text("❌ <b>Invalid Chat ID</b>\n\n<i>Must be a number (e.g., -1001234567890)</i>", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"❌ <b>Unable to Access Chat</b>\n<i>{e}</i>", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command("adddestination") & filters.private)
async def add_destination(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: <code>/adddestination -1001234567890</code>", parse_mode=enums.ParseMode.HTML)

    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    if not await db.check_premium(user_id):
        return await message.reply_text(
            "❌ <b>Premium Only Command</b>\n\n"
            "<i>/adddestination sirf premium users use kar sakte hain.</i>\n"
            "<i>Premium lene ke liye /premium use karein.</i>",
            parse_mode=enums.ParseMode.HTML
        )

    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid chat id.", parse_mode=enums.ParseMode.HTML)

    try:
        chat, member = await _validate_dump_destination(client, chat_id)
        await db.set_dump_chat(user_id, chat_id)
        await _send_destination_log(client, message.from_user, chat, chat_id, member)
    except Exception as exc:
        return await message.reply_text(
            f"❌ <b>Destination add nahi ho paaya.</b>\n<i>{exc}</i>",
            parse_mode=enums.ParseMode.HTML
        )

    await message.reply_text(
        f"✅ Destination set to <code>{chat_id}</code> ({chat.title or 'Private Chat'})",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command("removedestination") & filters.private)
async def remove_destination(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: <code>/removedestination -1001234567890</code>", parse_mode=enums.ParseMode.HTML)

    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid chat id.", parse_mode=enums.ParseMode.HTML)
    current = await db.get_dump_chat(user_id)
    if current != chat_id:
        return await message.reply_text(
            f"⚠️ Current destination is <code>{current}</code>. Provided chat id does not match.",
            parse_mode=enums.ParseMode.HTML
        )

    await db.set_dump_chat(user_id, None)
    await message.reply_text("✅ Destination removed.", parse_mode=enums.ParseMode.HTML)

# ======================================================
# Callbacks - Full Settings Navigation
# ======================================================
@Client.on_callback_query(filters.regex("^(cmd_list_btn|dump_chat_btn|thumb_btn|caption_btn|user_stats_btn|settings_back_btn|close_btn)$"))
async def settings_callbacks(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
   
    # Common back/close buttons
    back_close = [[InlineKeyboardButton("⬅️ Back", callback_data="settings_back_btn"), InlineKeyboardButton("❌ Close", callback_data="close_btn")]]
    if data == "cmd_list_btn":
        await callback_query.edit_message_text(
            COMMANDS_TXT,
            reply_markup=InlineKeyboardMarkup(back_close),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
    elif data == "dump_chat_btn":
        current = await db.get_dump_chat(user_id)
        if current:
            try:
                chat = await client.get_chat(current)
                title = chat.title or "Private Chat"
            except:
                title = "Unknown (Inaccessible)"
            text = (
                f"<b>🗑 Current Dump Chat</b>\n\n"
                f"<b>Chat ID:</b> <code>{current}</code>\n"
                f"<b>Title:</b> {title}\n\n"
                "<i>All saved files are forwarded here.</i>\n"
                "<i>Use /setchat to change or clear.</i>"
            )
        else:
            text = (
                "<b>🗑 No Dump Chat Set</b>\n\n"
                "<i>Saved files appear only in this chat.</i>\n"
                "<i>Use /setchat &lt;chat_id&gt; to enable forwarding.</i>"
            )
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_close), parse_mode=enums.ParseMode.HTML)
    elif data == "thumb_btn":
        thumb = await db.get_thumbnail(user_id)
        if thumb and os.path.exists(thumb):
            await callback_query.message.reply_photo(
                thumb,
                caption="<b>🖼 Your Current Custom Thumbnail</b>\n\n<i>Send a new photo to update • /del_thumb to remove</i>",
                parse_mode=enums.ParseMode.HTML
            )
            await callback_query.answer("Thumbnail preview sent below 👇")
        else:
            await callback_query.edit_message_text(
                "<b>🖼 No Custom Thumbnail Set</b>\n\n"
                "<i>Send a photo to set as default thumbnail for uploads.</i>",
                reply_markup=InlineKeyboardMarkup(back_close),
                parse_mode=enums.ParseMode.HTML
            )
    elif data == "caption_btn":
        caption = await db.get_caption(user_id)
        if caption:
            preview = caption.format(filename="Video_File_2024.mp4", size="1.2 GB")
            text = (
                f"<b>📝 Current Custom Caption</b>\n\n"
                f"<code>{caption}</code>\n\n"
                f"<b>Preview:</b>\n{preview}\n\n"
                "<i>Placeholders: {filename}, {size}</i>\n"
                "<i>/set_caption &lt;text&gt; to change • /del_caption to remove</i>"
            )
        else:
            text = (
                "<b>📝 No Custom Caption Set</b>\n\n"
                "<i>Use /set_caption &lt;text&gt; to set one.</i>\n"
                "<i>Supports {filename} and {size} placeholders.</i>"
            )
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_close), parse_mode=enums.ParseMode.HTML)
    elif data == "user_stats_btn":
        # Fetch real stats from DB
        is_premium = await db.check_premium(user_id)
        user_data = await db.col.find_one({'id': int(user_id)})
       
        if is_premium:
            limit_text = "♾️ Unlimited"
            usage_text = "Ignored (Premium)"
        else:
            # Free user logic
            daily_limit = 10
            used = user_data.get('daily_usage', 0)
            limit_text = f"{daily_limit} Files / 24h"
            usage_text = f"{used} / {daily_limit}"
        text = (
            f"<b>📊 My Usage Statistics</b>\n\n"
            f"<b>Plan:</b> {'💎 Premium' if is_premium else '👤 Free'}\n"
            f"<b>Daily Limit:</b> <code>{limit_text}</code>\n"
            f"<b>Today's Usage:</b> <code>{usage_text}</code>\n\n"
            f"<i>Upgrade to Premium for unlimited downloads!</i>"
        )
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_close), parse_mode=enums.ParseMode.HTML)
    elif data == "settings_back_btn":
        # Re-render main menu
        is_premium = await db.check_premium(user_id)
        premium_badge = "💎 Premium Member" if is_premium else "👤 Free User"
       
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Commands List", callback_data="cmd_list_btn")],
            [InlineKeyboardButton("📊 My Usage Stats", callback_data="user_stats_btn")],
            [InlineKeyboardButton("🗑 Dump Chat", callback_data="dump_chat_btn")],
            [
                InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb_btn"),
                InlineKeyboardButton("📝 Caption", callback_data="caption_btn")
            ],
            [InlineKeyboardButton("❌ Close Menu", callback_data="close_btn")]
        ])
       
        text = (
            f"<b>⚙️ Settings Panel</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Account:</b> {premium_badge}\n"
            f"<b>User ID:</b> <code>{user_id}</code>\n\n"
            f"<i>Select an option below to customize your experience.</i>"
        )
       
        await callback_query.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)
    elif data == "close_btn":
        await callback_query.message.delete()
    await callback_query.answer()
