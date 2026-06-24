# Пресеты конфигурации шаблона

Пресеты позволяют быстро сгенерировать проект с предсобранным набором интеграций для типовых сценариев использования.

При выборе пресета индивидуальные флаги (`add_sql_alchemy`, `add_kafka`, и т.д.) **игнорируются** — набор модулей определяется пресетом.

## Доступные пресеты

### `custom` (по умолчанию)

Ручная настройка. Набор модулей определяется индивидуальными флагами.

---

### `bff` — Backend For Frontend

Агрегирующий сервис, который обращается к нескольким внутренним сервисам и отдаёт данные фронтенду.

| Модуль | Включён |
|--------|---------|
| SQLAlchemy | ✗ |
| Redis (кэш) | ✓ |
| httpx (HTTP-клиент) | ✓ |
| GraphQL-клиент | ✓ |
| gRPC-клиент | ✓ |
| Kafka | ✗ |
| RabbitMQ | ✗ |
| Redis Streams | ✗ |
| MinIO | ✗ |

**Типичное применение:** API-шлюз для мобильного или веб-приложения, который агрегирует данные из сервисов на REST, GraphQL и gRPC.

---

### `crud` — CRUD REST API

Стандартный микросервис с базой данных и кэшем.

| Модуль | Включён |
|--------|---------|
| SQLAlchemy | ✓ |
| Redis (кэш) | ✓ |
| httpx | ✗ |
| GraphQL | ✗ |
| gRPC | ✗ |
| Kafka | ✗ |
| RabbitMQ | ✗ |
| Redis Streams | ✗ |
| MinIO | ✗ |

**Типичное применение:** Сервис пользователей, каталог товаров, сервис заказов — любой сервис с CRUD-операциями над базой данных.

---

### `worker-kafka` — Фоновый обработчик (Kafka)

Воркер, который потребляет сообщения из Kafka и сохраняет результаты в базу данных.

| Модуль | Включён |
|--------|---------|
| SQLAlchemy | ✓ |
| Redis (кэш) | ✗ |
| httpx | ✗ |
| GraphQL | ✗ |
| gRPC | ✗ |
| Kafka | ✓ |
| RabbitMQ | ✗ |
| Redis Streams | ✗ |
| MinIO | ✗ |

**Типичное применение:** Обработчик событий, сервис нотификаций, ETL-пайплайн.

---

### `worker-rabbitmq` — Фоновый обработчик (RabbitMQ)

Аналог `worker`, но в качестве брокера используется RabbitMQ.

| Модуль | Включён |
|--------|---------|
| SQLAlchemy | ✓ |
| Redis (кэш) | ✗ |
| httpx | ✗ |
| GraphQL | ✗ |
| gRPC | ✗ |
| Kafka | ✗ |
| RabbitMQ | ✓ |
| Redis Streams | ✗ |
| MinIO | ✗ |

**Типичное применение:** Обработчик задач с маршрутизацией через exchange, dead-letter очереди.

---

### `worker-redis` — Фоновый обработчик (Redis Streams)

Аналог `worker`, но в качестве брокера используется Redis Streams.

| Модуль | Включён |
|--------|---------|
| SQLAlchemy | ✓ |
| Redis (кэш) | ✗ |
| httpx | ✗ |
| GraphQL | ✗ |
| gRPC | ✗ |
| Kafka | ✗ |
| RabbitMQ | ✗ |
| Redis Streams | ✓ |
| MinIO | ✗ |

**Типичное применение:** Лёгкий обработчик событий, когда отдельный брокер нежелателен — Redis уже используется в инфраструктуре.

---

## Добавление компонента после генерации

Если вы выбрали пресет, а позднее потребовался дополнительный компонент — его можно добавить вручную за несколько шагов.

### Пример: добавить RabbitMQ к проекту на пресете `worker`

**1. Установите зависимость**

```bash
uv add "aio-pika>=9.5.5,<11.0.0"
```

**2. Скопируйте модули из шаблона**

Из директории `api/src/` репозитория шаблонизатора скопируйте в свой проект:

```
brokers/rabbitmq/              → src/brokers/rabbitmq/
config/rabbitmq_config.py      → src/config/rabbitmq_config.py
bases/brokers/base_message_broker.py         → src/bases/brokers/base_message_broker.py
bases/brokers/base_rabbitmq_routing_configurator.py → src/bases/brokers/...
models/dto/broker_message_dto.py             → src/models/dto/broker_message_dto.py
tools/di_containers/rabbitmq_di_container.py → src/tools/di_containers/rabbitmq_di_container.py
```

**3. Добавьте переменные окружения**

В `.env` / `.env.example` добавьте:

```env
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
```

**4. Добавьте конфигурацию в `app_config.py`**

```python
from config.rabbitmq_config import RabbitMQConfig

class AppConfig(BaseSettings):
    ...
    rabbitmq: RabbitMQConfig = RabbitMQConfig()
```

**5. Добавьте сервис в `docker-compose.yaml`**

Скопируйте секцию `services.rabbitmq` из `to_compose/rabbitmq.yaml` шаблона в ваш `docker-compose.yaml`.

**6. Подключите DI-контейнер**

В `tools/di_containers/app_container.py` добавьте:

```python
from tools.di_containers.rabbitmq_di_container import ProducerContainer, ConsumerContainer

class AppContainer(DeclarativeContainer):
    ...
    producer = ProducerContainer()
    consumer = ConsumerContainer()
```

---

Аналогичный алгоритм применяется для любого другого компонента — ориентируйтесь на соответствующий `docs/<компонент>.md` для деталей конфигурации.
