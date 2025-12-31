FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

COPY . .