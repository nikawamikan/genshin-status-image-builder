FROM python:3.11.4-alpine3.18

WORKDIR /usr/src
COPY requirements.txt .
COPY init.sh .

RUN sh init.sh && pip install --no-cache-dir -r requirements.txt