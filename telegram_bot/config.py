import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

owner_id_str = os.getenv("OWNER_ID", "0").strip()
if not owner_id_str:
    owner_id_str = "0"
OWNER_ID = int(owner_id_str)

OWNER_PIN = os.getenv("OWNER_PIN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
