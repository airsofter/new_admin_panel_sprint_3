# Админ-панель для кинотеатра

Проект представляет собой полноценную систему управления кинотеатром с ETL-процессом для синхронизации данных между PostgreSQL и Elasticsearch.

## 🏗️ Архитектура проекта

Проект состоит из нескольких компонентов:

- **Django API** - основное веб-приложение с REST API
- **ETL-сервис** - система переноса данных из PostgreSQL в Elasticsearch
- **PostgreSQL** - основная база данных
- **Elasticsearch** - поисковый движок для фильмов

## 📁 Структура проекта

```
├── etl/                    # ETL-сервис для синхронизации данных
│   ├── postgres_to_es/    # Основной код ETL
│   │   ├── main.py        # Точка входа ETL
│   │   ├── config.py      # Конфигурация
│   │   ├── backoff.py     # Декоратор для повторных попыток
│   │   └── ...
│   └── Dockerfile         # Образ для ETL-сервиса
├── project/               # Django приложения
│   ├── django_api/       # Основное Django приложение
│   └── simple_project/   # Дополнительные компоненты
├── docker-compose.yml    # Оркестрация всех сервисов
├── pyproject.toml        # Зависимости Poetry
└── README.md            # Этот файл
```

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.12+
- Poetry

### Установка и запуск

1. **Клонируйте репозиторий:**

   ```bash
   git clone <repository-url>
   cd new_admin_panel_sprint_3
   ```

2. **Установите зависимости:**

   ```bash
   poetry install
   ```

3. **Создайте файл .env:**

   ```bash
   cp .env.example .env
   # Отредактируйте переменные окружения
   ```

4. **Запустите все сервисы:**

   ```bash
   docker-compose up -d
   ```

5. **Проверьте статус сервисов:**

   ```bash
   docker-compose ps
   ```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` со следующими переменными:

```env
# PostgreSQL
POSTGRES_DB=theatre
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
SQL_HOST=localhost
SQL_PORT=5432

# Elasticsearch
ES_HOST=localhost
ES_PORT=9200
ELASTIC_USER=elastic
ELASTIC_PASSWORD=your_elastic_password

# Django
SECRET_KEY=your_secret_key
DEBUG=True
```

### Настройка ETL

ETL-сервис автоматически:

- Создает индекс `movies` в Elasticsearch
- Загружает данные из PostgreSQL
- Обрабатывает ошибки с помощью backoff-стратегии
- Сохраняет состояние для возобновления работы

## 📊 ETL-процесс

### Особенности реализации

- **Отказоустойчивость**: Использование backoff-стратегии для повторных попыток
- **Состояние**: Сохранение прогресса в файле `state/state.json`
- **Валидация**: Конфигурация через Pydantic
- **Логирование**: Подробные логи всех операций

### Схема данных Elasticsearch

Индекс `movies` содержит:

- Основную информацию о фильмах
- Вложенные объекты для актеров, режиссеров, сценаристов
- Полнотекстовый поиск с поддержкой русского и английского языков
- Оптимизированные поля для сортировки

## 🛠️ Разработка

### Локальная разработка

1. **Активируйте виртуальное окружение:**

   ```bash
   poetry shell
   ```

2. **Запустите только базы данных:**

   ```bash
   docker-compose up elasticsearch theatre-db -d
   ```

3. **Запустите Django локально:**

   ```bash
   cd project/django_api
   python manage.py runserver
   ```

4. **Запустите ETL локально:**

   ```bash
   cd etl/postgres_to_es
   python main.py
   ```

### Тестирование

```bash
# Запуск тестов Django
python manage.py test

# Проверка кода
flake8
black --check .
```

## 📚 API документация

После запуска Django API будет доступен по адресу:

- **Основной API**: <http://localhost:8000/api/>
- **Админ-панель**: <http://localhost:8000/admin/>

## 🔍 Мониторинг

### Логи сервисов

```bash
# Логи ETL
docker-compose logs etl

# Логи Elasticsearch
docker-compose logs elasticsearch

# Логи PostgreSQL
docker-compose logs theatre-db
```

### Проверка состояния Elasticsearch

```bash
curl -u elastic:your_password http://localhost:9200/_cluster/health
```

## 🛡️ Безопасность

- Все пароли хранятся в переменных окружения
- Elasticsearch защищен аутентификацией
- Django использует секретный ключ для безопасности

## 👥 Авторы

- **Denis** - [den-nd.96@mail.ru](mailto:den-nd.96@mail.ru)

---

**Примечание**: Для продакшена рекомендуется настроить дополнительные меры безопасности и мониторинга.
