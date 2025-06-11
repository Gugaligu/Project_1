# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем переменные среды в правильном формате
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаем и переходим в рабочую директорию
WORKDIR /app

# Устанавливаем зависимости системы и очищаем кеш
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Копируем только файлы зависимостей сначала для кэширования
COPY pyproject.toml poetry.lock /app/

# Устанавливаем зависимости проекта (без создания виртуального окружения)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Копируем весь проект
COPY . /app/


# Команда для запуска сервера Django
CMD ["python", "sitehotel/manage.py", "runserver", "0.0.0.0:8000"]