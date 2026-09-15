# petclinic-api-db-tests

Production-like фреймворк для API- и DB-автотестов Spring PetClinic REST. Цель проекта — показать полноценную backend-автоматизацию: Python + Pytest + Requests + SQL + PostgreSQL/MySQL + Docker. API проверяет бизнес-операцию, БД — фактический результат работы backend. Spring PetClinic REST — тестируемое приложение (AUT), запускается в Docker.

Главный сценарий:

```text
Pytest
  → OwnerApi / PetApi / VisitApi
  → BaseApiClient
  → Spring PetClinic REST
  → PostgreSQL / MySQL
  → DatabaseClient / Repository
  → SQL-проверка
```

Тест должен выглядеть примерно так:

```python
owner = owner_factory.build()

response = owner_api.create_owner(owner)
assert response.status_code == 201

created = owner_repository.get_by_id(response.json()["id"])

assert created["first_name"] == owner.first_name
assert created["last_name"] == owner.last_name
```

Никаких сырых `requests` и SQL внутри тестов без необходимости — для этого существуют API и DB слои.

## Ключевые архитектурные решения (важно не сломать)

- **API Object, а не сырые HTTP-вызовы.** `OwnerApi`/`PetApi`/`VisitApi` знают endpoints и операции ресурса; `BaseApiClient` знает HTTP transport. Тесты работают через API Object.
- **DB Client не знает бизнес-логику.** `DatabaseClient` отвечает за подключение, выполнение SQL, fetch, transactions и cleanup. SQL конкретных сущностей находится в Repository.
- **API и DB — две независимые проверки.** HTTP status/response проверяет API-результат, SQL проверяет фактическое состояние БД после работы backend. Не заменять одно другим.
- **Тестовые данные — через factories.** `OwnerFactory`/`PetFactory`/`VisitFactory` используют Faker и дают валидные значения с возможностью override. Не размазывать random data по тестам.
- **Fixtures управляют lifecycle.** Подготовка данных → тест → cleanup. Fixture может создавать данные через API или напрямую через SQL, если создание через API не является частью проверяемого сценария.
- **SQL только параметризованный.** Не собирать запросы через f-string/конкатенацию. Использовать параметры драйвера.
- **Тесты независимы.** Нельзя строить suite как цепочку зависимых тестов. E2E flow `create owner → create pet → create visit` допустим только как самостоятельный integration-сценарий.
- **PostgreSQL — первая реализация, MySQL — вторая.** Сначала полностью стабилизировать PostgreSQL, затем добавить MySQL. Database-specific различия не должны попадать в тесты без необходимости.
- **Конфигурация через окружение.** URL, credentials, DB host/port/password и прочие настройки — через `.env`. `.env` не коммитится, `.env.example` коммитится.
- **Docker — часть проекта.** PetClinic и PostgreSQL должны запускаться воспроизводимо через Docker Compose. Тесты не должны зависеть от локально установленного PostgreSQL.
- **Не использовать ORM для DB-проверок.** Цель проекта — показать работу с SQL и relational DB. Предпочтительно `psycopg`/MySQL driver → SQL → database.
- **Не считать поведение «типичным REST» автоматически правильным.** Опираться на актуальный API-контракт и фактическое поведение PetClinic. Расхождения фиксировать, а не маскировать.

## Структура

```text
config/                 настройки из .env
api/
  base_client.py        HTTP transport
  owner_api.py          endpoints Owners
  pet_api.py            endpoints Pets
  visit_api.py          endpoints Visits
db/
  client.py              DB transport
  repositories/
    owner_repository.py
    pet_repository.py
    visit_repository.py
models/                  Pydantic request/response models
factories/               Faker test data
assertions/              общие API/DB assertions
tests/
  owners/                CRUD + negative + DB validation
  pets/                  CRUD + relationships + DB validation
  visits/                CRUD + relationships + DB validation
  integration/            сквозные backend-сценарии
conftest.py              Pytest fixtures
docker-compose.yml       PetClinic + PostgreSQL/MySQL
.env.example             безопасная конфигурация
pyproject.toml           dependencies/lint/type-check
README.md                запуск и документация
```

Это целевая структура, а не чек-лист. Не создавать слой или файл, пока для него нет реальной функциональности.

## Запуск

```bash
docker compose up -d

pytest
pytest -m smoke
pytest -m integration
pytest -m db
pytest -m "not slow"
```

Для локальной разработки тесты могут запускаться из Python environment, а PetClinic и БД — в Docker.

Основные настройки:

```text
API_BASE_URL=http://localhost:9966/petclinic
DB_HOST=localhost
DB_PORT=5432
DB_NAME=petclinic
DB_USER=petclinic
DB_PASSWORD=petclinic
DB_ENGINE=postgres
```

## Конвенции

- `config` ничего внутреннего не импортирует — лист графа зависимостей.
- `api` не выполняет SQL, `db` не выполняет HTTP.
- Assertions находятся в тестах или assertion helpers, но не в client/repository.
- SQL должен быть читаемым и параметризованным.
- Fixtures отвечают за lifecycle, а не за бизнес-логику.
- Маркеры используются осмысленно: `smoke`, `positive`, `negative`, `integration`, `db`, `slow`.
- Secrets никогда не находятся в коде, тестах или commit history.
- Не добавлять технологию только ради демонстрации. Каждый слой должен иметь конкретную роль.

## Процесс добавления фичи

1. Определить API-операцию и ожидаемое состояние БД.
2. Решить, какой слой отвечает за каждую часть.
3. Добавить/обновить model и factory при необходимости.
4. Реализовать API/DB слой.
5. Добавить тест и DB validation.
6. Добавить cleanup.
7. Прогнать конкретный тест, затем весь соответствующий suite.
8. Прогнать lint/type-check, если настроены.
9. Обновить README, если изменился способ запуска или поведения.

## Текущий статус / не-цели

Репозиторий собирается с нуля.

Планируемые стадии:

```text
Docker/PetClinic
→ PostgreSQL
→ API client
→ API Objects
→ models/factories
→ DB client/repositories
→ fixtures
→ API + DB validation
→ integration tests
→ MySQL
→ Allure
→ CI
```

Не считать запланированную функциональность реализованной, пока она реально не существует и не проверена.

Вне scope: UI/Selenium/Playwright, frontend-автоматизация, Kubernetes, Kafka/Redis и другие инфраструктурные компоненты, не требуемые для API + DB testing.