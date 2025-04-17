FROM python:3.10-slim

WORKDIR /app
RUN sudo apt install -y wireguard-tools

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "vpn_backend.wsgi:application", "--bind", "0.0.0.0:8000"]