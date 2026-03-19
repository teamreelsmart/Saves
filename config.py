"""
Save Restricted Content Bot Configuration

Developed by: LastPerson07Xcantarella
Telegram: @cantarellabots X @THEUPDATEDGUYS

Please retain this credit if you use or modify this project.
"""

import os
import re


# ==============================
# Telegram Bot Credentials
# ==============================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", "31024360"))
API_HASH = os.environ.get("API_HASH", "8419dab9aac814d0dd1f0a9ed3e63a3e")


# ==============================
# Admin Configuration
# ==============================

# Add admin user IDs in env: comma/space/newline supported (example: "12345, 67890")
def _parse_admin_ids(raw_admins: str):
    admin_ids = []
    for token in re.split(r"[\s,]+", raw_admins.strip()):
        if not token:
            continue
        token = token.strip().strip("[]")
        if token.startswith("@"):
            token = token[1:]
        if token.isdigit():
            admin_ids.append(int(token))
    return admin_ids


ADMINS = _parse_admin_ids(os.environ.get("ADMINS", ""))


# ==============================
# Database Configuration
# ==============================

DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "SaveRestricted2")


# ==============================
# Logging Configuration
# ==============================

# Replace with your Telegram log channel ID (example: -1001234567890)
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))


# ==============================
# Error Handling
# ==============================

# Set to True to send error messages to users
ERROR_MESSAGE = os.environ.get("ERROR_MESSAGE", "True").lower() == "true"
