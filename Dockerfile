FROM python:3.11.4-alpine3.18

WORKDIR /usr/src/app
COPY requirements.txt .
COPY init.sh .

RUN apk update && apk add --no-cache gcc g++ libffi-dev
RUN pip install --no-cache-dir -r requirements.txt