import sys

file_path = "telegram_bot/database/db.py"
with open(file_path, "r") as f:
    content = f.read()

content = content.replace("DB_NAME", "get_db_path()")

with open(file_path, "w") as f:
    f.write(content)
