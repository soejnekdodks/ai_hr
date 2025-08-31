# Registration Bot | Бот для регистрации на мероприятия

<h1 align="center">Registration Bot</h1>
<div><h4 align="center"><a href="#-быстрый-старт">Установка</a> · <a href="#-разработка">Разработка</a> · <a href="#функционал">Функции</a> · <a href="#технологии">Технологии</a></h4></div>

<div align="center">
  <a href="https://www.python.org/">
    <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white&style=for-the-badge" />
  </a>
  <a href="https://docs.aiogram.dev/">
    <img alt="Aiogram" src="https://img.shields.io/badge/Aiogram-3.x-green?logo=telegram&logoColor=white&style=for-the-badge" />
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

Telegram-бот для удобной регистрации на мероприятиях с двусторонней функциональностью: каждый пользователь может быть как организатором, так и участником мероприятий.

## 🚀 Быстрый старт

### Предварительные требования

- [Docker](https://docs.docker.com/get-docker/) и Docker Compose
- [Poetry](https://python-poetry.org/) (для разработки)

### Настройка окружения

1. Скопируйте файл окружения:
   ```bash
   cp example.env .env
   ```

2. Отредактируйте `.env` файл, добавив необходимые параметры:
   ```env
   TG_TOKEN=your_telegram_bot_token_here
   DATABASE_URL=postgresql://user:password@db:5432/registration_bot
   # Другие параметры...
   ```

> В целом для запуска достаточно заполнить `TG_TOKEN`. Остальные параметры можно не заполнять, но тогда безопасность вашей базы данных будет под вопросом, так что в соответствии с соглашением [RFC](https://datatracker.ietf.org/doc/html/rfc2119.html) скажу что это правило соответствует пунктам `SHOULD` или `RECOMMENDED`

### Запуск приложения

#### Для production-окружения
```bash
make up-prod
```

#### Для development-окружения
```bash
make up
```

## ⚙️ Функционал

### 👥 Для участников
- 🔍 Поиск мероприятий по ID
- 🎯 Фильтрация мероприятий по интересам
- 📝 Запись на мероприятия (и отмена записи)
- 📋 Просмотр записанных мероприятий
- ⏰ Напоминания за день и за час до начала

### 🎪 Для организаторов
- ➕ Создание новых мероприятий
- 👀 Просмотр администрируемых мероприятий
- ✏️ Редактирование существующих мероприятий
- 🗑️ Удаление мероприятий

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
| `make build` | Пересобрать проект без запуска |
| `make up` | Пересобрать и запустить в dev-режиме |
| `make up-prod` | Пересобрать и запустить в prod-режиме |
| `make test` | Запустить тесты в контейнере |
| `make clear` | Удаление volumes и очистка |
| `make format` | Форматирование кода |
| `make lint` | Проверка кода линтером |
| `make fix` | Автоматическое исправление проблем |
| `make typecheck` | Проверка типов с помощью pyright |
| `make git` | Комплексная проверка перед коммитом |

### 🏗️ Структура проекта

```
registration-bot/
├── src/ # Исходный код приложения
├── tests/ # Тесты
├── Makefile # Управление задачами
├── pyproject.toml # Конфигурация Poetry
├── docker-compose.yml # Docker Compose конфигурация
├── docker-compose-prod.yml # Docker Compose конфигурация
└── docker-compose-test.yml # Docker Compose конфигурация
```

## 🤝 Contributing
Развитием проекта занимаются разработчики, и мешать им не надо ~а иначе будем громко ругаться~. Лучше оставьте в issue свои пожелания и репорты о найденых багах.

## 📝 Лицензия
Разработка лицензии находится в процессе, т.к. наши юристы пока не нашли похожей статьи на КонсультатнПлюс

## 📞 Поддержка
Если у вас возникли вопросы или проблемы:
- Создайте issue в репозитории
- Напишите нам на почту SomeUnworkEmail@gmail.com

---

<div align="center">
  <sub>Сделано с ❤️ для удобной организации мероприятий</sub>
</div>
