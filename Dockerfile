FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY telegram_bot/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot source code
COPY telegram_bot/ ./telegram_bot/

# Setup timezone if needed
ENV TZ=Asia/Jakarta

# Run the bot
WORKDIR /app/telegram_bot
CMD ["python", "-u", "bot.py"]
