FROM python:3.12-alpine

# системні утиліти (ping)
RUN apk add --no-cache iputils tzdata

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ping_bot.py .

# history буде тут
RUN mkdir -p /data

ENV HISTORY_FILE=/data/history.log
ENV PYTHONUNBUFFERED=1

VOLUME ["/data"]

CMD ["python", "ping_bot.py"]
