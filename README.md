# AI HR | Сервис автоматического проведения собеседований

<h1 align="center">AI HR</h1>
<div><h4 align="center"><a href="#-быстрый-старт">Установка</a> · <a href="#-разработка">Разработка</a> · <a href="#функционал">Функции</a> · <a href="#технологии">Технологии</a></h4></div>

<div align="center">
  <a href="https://www.python.org/">
    <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white&style=for-the-badge" />
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.95+-red?logo=fastapi&logoColor=white&style=for-the-badge" />
  </a>
  <a href="https://www.docker.com/">
    <img alt="Docker" src="https://img.shields.io/badge/Docker-✓-blue?logo=docker&logoColor=white&style=for-the-badge" />
  </a>
  <a href="https://python-poetry.org/">
    <img alt="Poetry" src="https://img.shields.io/badge/Poetry-✓-orange?logo=poetry&logoColor=white&style=for-the-badge" />
  </a>
</div>

<hr>

## 📖 Описание

AI HR

## 🚀 Быстрый старт

### Предварительные требования

- [Docker](https://docs.docker.com/get-docker/) и Docker Compose
- [Poetry](https://python-poetry.org/) (для разработки)
- [Front](https://github.com/tikhonlym/VTB-hackaton)

### Настройка окружения

1. Скопируйте файл окружения:
   ```bash
   cp example.env .env
   ```

2. Отредактируйте `.env` файл, добавив необходимые параметры:
   ```env
   # Другие параметры...
   ```

### Запуск приложения

```bash
make up
```

## ⚙️ Функционал

### 👥 Для клиентов
- Удобный интерфейс для телефона
- Голосовой ввод
- Фидбек по резюме
- Фидбек по собеседованию

### 🎪 Для организаторов
- Анализ соответствия резюме для вакансии
- Автоматическое проведение собеседования
- Анализ прохождения собеседования


## 🛠 Разработка

### Установка зависимостей

```bash
# Основные зависимости
poetry install

# С дополнительными инструментами для разработки
poetry install --with dev

# Если нужно добавить обязательную зависимость
poetry add package_name

# Если нужно добавить зависимость для разработки
poetry add --dev package_name
```

### 🛠️ Команды для разработки

| Команда | Описание |
|---------|----------|
| `make up` | Пересобрать и запустить в dev-режиме |
| `make format` | Форматирование кода |
| `make lint` | Проверка кода линтером |
| `make fix` | Автоматическое исправление проблем |
| `make typecheck` | Проверка типов с помощью pyright |
| `make git` | Комплексная проверка перед коммитом |

### 🏗️ Структура проекта

```
ai_hr/
├── app/ # API сервис, парсер резюме, генератор отчётов
├── cv_ai/ # Модель для анализа резюме
├── llm/ # Модель для генерации вопросов и анализа ответов
├── Makefile # Управление автоматизация ввода команд
├── pyproject.toml # Конфигурация Poetry
└── docker-compose.yml # Docker Compose конфигурация
```

---

<div align="center">
  <sub>Сделано с ❤️ для удобного проведения собеседований </sub>
</div>
