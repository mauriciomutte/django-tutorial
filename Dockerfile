FROM python:3.12-slim

WORKDIR /app

# Installs pip
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . ./
