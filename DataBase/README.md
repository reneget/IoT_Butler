# 📡 Database API Service - REST API для управления данными

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-green.svg)

**REST API сервис для работы с базой данных пользователей и устройств**

[📖 Документация](#документация) • [🚀 Быстрый старт](#быстрый-старт) • [📡 API Endpoints](#api-endpoints)

</div>

---

## 📋 Содержание

- [Описание](#описание)
- [Архитектура](#архитектура)
- [Модели данных](#модели-данных)
- [Быстрый старт](#быстрый-старт)
- [API Endpoints](#api-endpoints)
- [Конфигурация](#конфигурация)
- [Разработка](#разработка)

---

## 🎯 Описание

Database API Service — это REST API сервис на базе **FastAPI**, который предоставляет полный набор операций для работы с пользователями и устройствами. Сервис использует **SQLAlchemy** для работы с **PostgreSQL** и следует принципам чистой архитектуры.

### Основные возможности

- ✅ CRUD операции для пользователей
- ✅ CRUD операции для устройств
- ✅ Валидация данных через Pydantic
- ✅ Автоматическая документация API (Swagger/OpenAPI)
- ✅ Healthcheck endpoint
- ✅ Репозиторный паттерн для работы с БД
- ✅ Логирование всех операций

---

## 🏗️ Архитектура

### Схема работы API

```mermaid
graph TB
    A[Client Request] -->|HTTP| B[FastAPI Router]
    B --> C[Pydantic Validation]
    C --> D{Valid?}
    D -->|No| E[400 Bad Request]
    D -->|Yes| F[Repository Layer]
    F --> G[SQLAlchemy ORM]
    G --> H[(PostgreSQL)]
    H -->|Data| G
    G -->|Model| F
    F -->|Pydantic Model| B
    B -->|JSON Response| A
    
    style A fill:#0088cc,color:#fff
    style B fill:#009688,color:#fff
    style C fill:#4ecdc4,color:#fff
    style F fill:#45b7d1,color:#fff
    style G fill:#96ceb4,color:#fff
    style H fill:#feca57,color:#000
```

### Архитектура слоев

```mermaid
graph TD
    A[API Layer<br/>routs/] --> B[Pydantic Models<br/>Validation]
    A --> C[Repository Layer<br/>repositories/]
    C --> D[Database Models<br/>models/]
    C --> E[Database Connection<br/>core/]
    E --> F[(PostgreSQL)]
    
    B -->|Request/Response| A
    D -->|ORM Mapping| C
    E -->|Connection Pool| C
    
    style A fill:#ff6b6b,color:#fff
    style B fill:#4ecdc4,color:#fff
    style C fill:#45b7d1,color:#fff
    style D fill:#96ceb4,color:#fff
    style E fill:#feca57,color:#000
```

### Поток обработки запроса

```mermaid
sequenceDiagram
    participant Client as 📱 Client
    participant Router as 🛣️ Router
    participant Validator as ✅ Pydantic
    participant Repo as 📦 Repository
    participant DB as 🗄️ PostgreSQL
    
    Client->>Router: POST /device/create/device
    Router->>Validator: Validate DeviceCreate
    Validator-->>Router: Valid data
    
    Router->>Repo: create_device(**data)
    Repo->>DB: INSERT INTO Devices
    DB-->>Repo: Device record
    Repo->>Repo: Convert to Model
    Repo-->>Router: Device model
    
    Router->>Validator: Convert to Pydantic
    Validator-->>Router: Device response
    Router-->>Client: 200 OK + JSON
```

---

## 📊 Модели данных

### Модель User

```python
class Users(Base):
    id: int                    # Primary key
    user_id: int              # Telegram User ID (unique)
    tag: str                  # Username
    devices: List[int]         # Array of device IDs
    device_counter: int        # Count of devices
    active: bool              # Account status
    create_time: datetime      # Registration time
```

### Модель Device

```python
class Devices(Base):
    device_id: int            # Primary key
    title: str                # Device name
    description: str          # Device description
    address: str              # Device IP/address
    active: bool              # Device status
    create_time: datetime     # Creation time
```

### ER-диаграмма

```mermaid
erDiagram
    Users ||--o{ Devices : "has many"
    
    Users {
        int id PK
        int user_id UK "Telegram ID"
        string tag
        int[] devices "Array of device IDs"
        int device_counter
        boolean active
        datetime create_time
    }
    
    Devices {
        int device_id PK
        string title
        string description
        string address
        boolean active
        datetime create_time
    }
```

---

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.10+
- PostgreSQL 13+ (или Docker)
- Запущенная база данных PostgreSQL

### Установка

1. **Установите зависимости:**
```bash
cd DataBase
pip install -r requirements.txt
```

2. **Настройте переменные окружения:**

Создайте файл `.env` или установите переменные окружения:

```env
DATABASE_URL=postgresql://admin:admin@localhost:5432/mydatabase
POSTGRES_DB=mydatabase
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
```

3. **Запустите сервис:**
```bash
python main.py
```

Сервис будет доступен по адресу: http://localhost:8000

### Запуск через Docker

```bash
# Из корневой директории проекта
docker compose up database -d
```

### Автоматическое создание таблиц

При первом запуске сервис автоматически создает все необходимые таблицы в базе данных через `create_tables()`.

---

## 📡 API Endpoints

### User Endpoints

| Метод | Путь | Описание | Тело запроса |
|-------|------|----------|--------------|
| POST | `/user/create/user` | Создать пользователя | `UserCreate` |
| GET | `/user/get/user/{user_id}` | Получить пользователя по ID | - |
| GET | `/user/get/all/users` | Получить всех пользователей | - |
| PUT | `/user/update/user/{user_id}` | Обновить пользователя | `UserUpdate` |
| DELETE | `/user/delete/user/{user_id}` | Удалить пользователя | - |
| GET | `/user/health` | Healthcheck | - |

### Device Endpoints

| Метод | Путь | Описание | Тело запроса |
|-------|------|----------|--------------|
| POST | `/device/create/device` | Создать устройство | `DeviceCreate` |
| GET | `/device/get/device/{device_id}` | Получить устройство по ID | - |
| GET | `/device/get/all/devices` | Получить все устройства | - |
| PUT | `/device/update/device/{device_id}` | Обновить устройство | `DeviceUpdate` |
| DELETE | `/device/delete/device/{device_id}` | Удалить устройство | - |

### Swagger документация

После запуска сервиса доступна автоматическая документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📝 Примеры запросов

### Создание пользователя

```bash
curl -X POST "http://localhost:8000/user/create/user" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123456789,
    "tag": "username",
    "devices": [],
    "device_counter": 0,
    "active": true,
    "create_time": "2025-12-02T10:00:00"
  }'
```

**Ответ:**
```json
{
  "id": 1,
  "user_id": 123456789,
  "tag": "username",
  "devices": [],
  "device_counter": 0,
  "active": true,
  "create_time": "2025-12-02T10:00:00"
}
```

### Создание устройства

```bash
curl -X POST "http://localhost:8000/device/create/device" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Умная лампа",
    "description": "Лампа в гостиной",
    "address": "192.168.1.50",
    "active": false,
    "create_time": "2025-12-02T10:00:00"
  }'
```

### Получение всех пользователей

```bash
curl -X GET "http://localhost:8000/user/get/all/users"
```

### Обновление пользователя

```bash
curl -X PUT "http://localhost:8000/user/update/user/123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "active": false
  }'
```

---

## ⚙️ Конфигурация

### Структура конфигурации

```python
class DatabaseConfig:
    url: str              # Database connection URL
    echo: bool            # SQLAlchemy echo mode

class Config:
    database: DatabaseConfig
```

### Переменные окружения

| Переменная | Описание | Обязательная | По умолчанию |
|------------|----------|--------------|--------------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ Да | - |
| `POSTGRES_DB` | Имя базы данных | ✅ Да | mydatabase |
| `POSTGRES_USER` | Пользователь БД | ✅ Да | admin |
| `POSTGRES_PASSWORD` | Пароль БД | ✅ Да | admin |
| `LOG_LEVEL` | Уровень логирования | ❌ Нет | INFO |
| `LOG_FILE` | Путь к файлу логов | ❌ Нет | /app/logs/app.log |

### Формат DATABASE_URL

```
postgresql://[user]:[password]@[host]:[port]/[database]
```

Пример:
```
postgresql://admin:admin@postgres:5432/mydatabase
```

---

## 🔧 Разработка

### Структура проекта

```
DataBase/
├── API/                  # REST API слой
│   ├── routs/           # API маршруты
│   │   ├── user.py      # User endpoints
│   │   ├── device.py    # Device endpoints
│   │   └── pydantic_models.py  # Pydantic схемы
│   └── utils/           # Утилиты API
│       └── api_functions.py
├── DataBase/            # Слой работы с БД
│   ├── core/            # Ядро БД
│   │   └── db_connection.py  # Подключение и сессии
│   ├── models/          # SQLAlchemy модели
│   │   ├── users_model.py
│   │   └── devices_model.py
│   └── repositories/    # Репозитории
│       ├── users_repo.py
│       └── devices_repo.py
├── configurations/      # Конфигурация
│   ├── __init__.py
│   ├── config.py        # Основная конфигурация
│   └── env_conf.py      # Загрузка переменных окружения
├── log/                 # Логирование
│   ├── __init__.py
│   └── config.py        # Настройка логирования
├── main.py             # Точка входа
├── requirements.txt    # Зависимости
└── Dockerfile          # Docker образ
```

### Добавление нового endpoint

1. **Создайте Pydantic модель:**
```python
# API/routs/pydantic_models.py
class NewEntityCreate(BaseModel):
    field1: str
    field2: int
```

2. **Создайте модель БД:**
```python
# DataBase/models/new_entity_model.py
class NewEntity(Base):
    __tablename__ = 'new_entity'
    id = Column(Integer, primary_key=True)
    field1 = Column(String)
    field2 = Column(Integer)
```

3. **Создайте репозиторий:**
```python
# DataBase/repositories/new_entity_repo.py
class NewEntityRepo:
    def create_entity(self, **kwargs):
        # Implementation
        pass
```

4. **Создайте endpoint:**
```python
# API/routs/new_entity.py
@router.post('/create/entity')
async def create_entity(entity: NewEntityCreate, db: Session = Depends(get_db)):
    repo = NewEntityRepo(db)
    created = repo.create_entity(**entity.__dict__)
    return NewEntity(**created.__dict__)
```

5. **Подключите роутер в main.py:**
```python
from API.routs import new_entity
app.include_router(new_entity.router)
```

### Логирование

Логи сохраняются в:
- `logs/app.log` — общие логи
- `logs/app_errors.log` — ошибки

Все операции логируются с уровнем INFO и выше.

---

## 📊 Статистика

```mermaid
pie title Распределение функциональности
    "User Management" : 40
    "Device Management" : 40
    "Database Layer" : 15
    "Validation" : 5
```

---

## 🔍 Репозиторный паттерн

Сервис использует репозиторный паттерн для абстракции работы с БД:

```python
class UserRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, **kwargs):
        # Создание пользователя
        pass
    
    def get_user_by_id(self, user_id: int):
        # Получение пользователя
        pass
    
    def get_all_users(self):
        # Получение всех пользователей
        pass
    
    def update_user(self, user_id: int, **kwargs):
        # Обновление пользователя
        pass
    
    def delete_user(self, user_id: int):
        # Удаление пользователя
        pass
```

Преимущества:
- ✅ Изоляция логики работы с БД
- ✅ Легкое тестирование
- ✅ Возможность замены реализации

---

## 🧪 Тестирование

### Healthcheck

Проверка работоспособности сервиса:

```bash
curl http://localhost:8000/user/health
```

**Ожидаемый ответ:**
```json
{
  "status": "OK"
}
```

### Тестирование через Swagger

1. Откройте http://localhost:8000/docs
2. Выберите endpoint
3. Нажмите "Try it out"
4. Заполните параметры
5. Нажмите "Execute"

---

## 🐛 Отладка

### Частые проблемы

1. **Ошибка подключения к БД:**
   - Проверьте `DATABASE_URL`
   - Убедитесь, что PostgreSQL запущен
   - Проверьте учетные данные

2. **Таблицы не создаются:**
   - Проверьте права доступа к БД
   - Проверьте логи при запуске
   - Убедитесь, что `create_tables()` вызывается

3. **Ошибки валидации:**
   - Проверьте формат данных в запросе
   - Убедитесь, что все обязательные поля заполнены
   - Проверьте типы данных

---

## 📚 Дополнительные ресурсы

- [FastAPI документация](https://fastapi.tiangolo.com/)
- [SQLAlchemy документация](https://docs.sqlalchemy.org/)
- [Pydantic документация](https://docs.pydantic.dev/)
- [PostgreSQL документация](https://www.postgresql.org/docs/)
- [Основной README проекта](../README.md)

---

<div align="center">

**Сделано с ❤️ для надежной работы с данными**

</div>

