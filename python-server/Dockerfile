FROM python:3.12-slim

ARG APP_PORT=5000
EXPOSE ${APP_PORT}

ENV APP_PORT=${APP_PORT}

WORKDIR /app

COPY server.py /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

CMD ["python", "server.py"]