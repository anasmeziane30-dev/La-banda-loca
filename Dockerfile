FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# تثبيت الحزم المطلوبة مباشرة وبدون استخدام requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir discord.py yt-dlp PyNaCl

COPY . .

CMD ["python", "bot.py"]
