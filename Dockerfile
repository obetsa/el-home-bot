FROM python:3.12-alpine

# системні утиліти (ping)
RUN apk add --no-cache iputils tzdata

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ping_bot.py .

# history буде тут
VOLUME ["/data"]

ENV PYTHONUNBUFFERED=1

CMD ["python", "ping_bot.py"]
