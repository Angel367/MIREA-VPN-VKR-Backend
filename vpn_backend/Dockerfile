FROM python:3.10-slim

# Установка дополнительных пакетов
RUN apt-get update && apt-get install -y \
    wireguard \
    wireguard-tools \
    iproute2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "vpn_backend.wsgi:application", "--bind", "0.0.0.0:8000"]