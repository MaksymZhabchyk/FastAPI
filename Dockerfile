FROM python:3.10-slim

WORKDIR /app

# 1. Встановлюємо саму утиліту poetry
RUN pip install poetry

# 2. Копіюємо файли конфігурації poetry
COPY pyproject.toml poetry.lock ./

# 3. Встановлюємо всі залежності через poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# 4. Копіюємо ВСЕ з папки app у корінь робочої папки контейнера
COPY ./app/ /app/

EXPOSE 8000

# Запускаємо з явним вказанням робочої директорії
CMD ["python", "main.py"]