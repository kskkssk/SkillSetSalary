FROM python:3.9-slim

WORKDIR /app

COPY app/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./app /app/
COPY worker /app/worker

ENV PYTHONPATH=/app

CMD ["python", "telegram_bot/tg_bot.py"]