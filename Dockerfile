FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Браузеры уже установлены в этом образе ✔
# playwright install НЕ нужен

COPY scraper.py .
COPY .env .

RUN mkdir -p /app/state

ENV PYTHONUNBUFFERED=1

CMD ["python", "scraper.py"]
