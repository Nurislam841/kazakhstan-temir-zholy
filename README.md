# KTZh Backend API

Backend API для системы перевозки багажей АО «НК «Қазақстан темір жолы».

## Технологии

- **FastAPI** - современный асинхронный веб-фреймворк
- **SQLAlchemy 2.0** - ORM с поддержкой async
- **Pydantic v2** - валидация данных
- **JWT** - аутентификация
- **SQLite/PostgreSQL** - база данных

## Установка

### 1. Создайте виртуальное окружение

```bash
cd backend
python -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Настройте переменные окружения

```bash
cp .env.example .env
# Отредактируйте .env файл
```

### 4. Запустите сервер

```bash
# Режим разработки:
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Или через Python:
python main.py
```

## API Документация

После запуска сервера документация доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Структура проекта

```
backend/
├── app/
│   ├── api/                 # API роутеры
│   │   ├── __init__.py
│   │   ├── auth.py         # Авторизация
│   │   ├── documents.py    # Документы
│   │   └── forms.py        # Формы ЛУ-59, ЛУ-63, ГУ-26
│   ├── core/               # Ядро приложения
│   │   ├── __init__.py
│   │   ├── config.py       # Конфигурация
│   │   ├── database.py     # База данных
│   │   └── security.py     # JWT, хэширование
│   ├── models/             # SQLAlchemy модели
│   │   ├── __init__.py
│   │   └── models.py
│   ├── schemas/            # Pydantic схемы
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/           # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── document_service.py
│   └── __init__.py
├── tests/                  # Тесты
├── main.py                 # Точка входа
├── requirements.txt        # Зависимости
├── .env                    # Переменные окружения
└── .env.example           # Пример .env
```

## API Endpoints

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/login` | Вход в систему |
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/refresh` | Обновление токена |
| GET | `/api/auth/me` | Текущий пользователь |
| POST | `/api/auth/logout` | Выход |

### Документы

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/documents` | Поиск документов |
| GET | `/api/documents/{id}` | Получить документ |
| POST | `/api/documents` | Создать документ |
| PATCH | `/api/documents/{id}` | Обновить документ |
| POST | `/api/documents/{id}/pay` | Подтвердить оплату |

### Формы

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/forms/lu63` | Создать ЛУ-63 |
| POST | `/api/forms/lu59` | Создать ЛУ-59 |
| POST | `/api/forms/gu26` | Создать ГУ-26 |

## Примеры запросов

### Регистрация

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ТОО Тест",
    "bin": "123456789012",
    "email": "test@example.com",
    "phone": "+77771234567",
    "password": "password123",
    "confirm_password": "password123"
  }'
```

### Вход

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "track_number": "123456789012",
    "password": "password123"
  }'
```

### Поиск документов

```bash
curl -X GET "http://localhost:8000/api/documents?page=1&limit=10" \
  -H "Authorization: Bearer <token>"
```

## База данных

### SQLite (разработка)

По умолчанию используется SQLite. База данных создается автоматически при первом запуске.

### PostgreSQL (продакшен)

Для использования PostgreSQL:

1. Установите PostgreSQL
2. Создайте базу данных:
   ```sql
   CREATE DATABASE ktzh;
   ```
3. Обновите `DATABASE_URL` в `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ktzh
   ```

## Тестирование

```bash
pytest
```

## Продакшен

Для продакшена рекомендуется:

1. Использовать PostgreSQL
2. Установить надежный `SECRET_KEY`
3. Отключить `DEBUG`
4. Настроить HTTPS
5. Использовать Gunicorn + Uvicorn workers:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```
