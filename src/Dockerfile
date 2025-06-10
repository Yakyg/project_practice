FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data.json bot.py ./

ENV TELEGRAM_TOKEN=""

CMD ["python", "bot.py"]
