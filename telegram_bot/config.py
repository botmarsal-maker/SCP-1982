import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
OWNER_PIN = os.getenv("OWNER_PIN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
