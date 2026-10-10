FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY common /app/common
COPY data /app/data

ENV PYTHONPATH=/app

CMD ["python", "-m", "server.accounts_server.server"]