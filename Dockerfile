FROM python:3.11.4-alpine3.18

WORKDIR /usr/src/app
COPY requirements.txt .
COPY init.sh .

RUN sh init.sh
RUN pip install --no-cache-dir -r requirements.txt