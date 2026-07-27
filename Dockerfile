FROM python:3.10

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir discord.py yt-dlp PyNaCl

COPY . .

CMD ["python", "bot.py"]
