import os
import time
from dotenv import load_dotenv

load_dotenv()

START_TIME = time.time()
VERSION = "1.0.0"

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

owner_id_str = os.getenv("OWNER_ID", "0").strip()
if not owner_id_str:
    owner_id_str = "0"

if "," in owner_id_str:
    OWNER_IDS = [int(x.strip()) for x in owner_id_str.split(",") if x.strip().isdigit() or (x.strip().startswith("-") and x.strip()[1:].isdigit())]
else:
    OWNER_IDS = [int(owner_id_str)]

# Keep OWNER_ID for fallback if needed, but prefer OWNER_IDS
OWNER_ID = OWNER_IDS[0] if OWNER_IDS else 0

OWNER_PIN = os.getenv("OWNER_PIN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
