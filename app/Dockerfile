FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

COPY /etc/ssl/PRIVATE.key /app
COPY /etc/ssl/PUBLIC.pem /app

EXPOSE 8443

