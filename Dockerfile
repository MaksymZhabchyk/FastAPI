FROM python:3.10-slim

WORKDIR /app

# Встановлюємо залежності
RUN pip install fastapi uvicorn email-validator

# Копіюємо ВСЕ з папки app у корінь робочої папки контейнера
COPY ./app/ /app/

EXPOSE 8000

# Запускаємо з явним вказанням робочої директорії
CMD ["python", "main.py"]