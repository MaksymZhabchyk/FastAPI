FROM python:3.10-slim

WORKDIR /app

# Встановлюємо залежності
RUN pip install fastapi uvicorn

# Копіюємо ВСЕ з папки app у корінь робочої папки контейнера
COPY ./app/ /app/

EXPOSE 8000

# Запускаємо з явним вказанням робочої директорії
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]