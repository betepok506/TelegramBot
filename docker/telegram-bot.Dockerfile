FROM python:3.9-slim

WORKDIR app
COPY ./telegram_bot telegram_bot
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --upgrade -r telegram_bot/requirements.txt

CMD python telegram_bot/src/bot.py