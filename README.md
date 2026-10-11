# spring-petclinic-api-sql-framework

Фреймворк API- и DB-автотестов для [Spring PetClinic REST](https://github.com/spring-petclinic/spring-petclinic-rest).

Идея проекта: **API проверяет бизнес-операцию, база данных — фактический результат работы backend**. Тест отправляет HTTP-запрос, проверяет ответ, а затем отдельным SQL-запросом убеждается, что данные действительно оказались в БД. Это две независимые проверки, и одна не заменяет другую.

Стек: Python 3.13, Pytest, Requests, Pydantic, Faker, SQL (psycopg / PyMySQL), PostgreSQL и MySQL, Docker Compose, Allure, GitHub Actions.

## Как выглядит тест

```python
def test_create_owner(owner_api, owner_factory, owner_repository, created_owner_ids):
    owner = owner_factory.build()

    response = owner_api.create_owner(owner.to_payload())
    assert response.status_code == 201
    created_owner_ids.append(response.json()["id"])

    row = owner_repository.get_by_id(response.json()["id"])
    assert row["first_name"] == owner.first_name
    assert row["last_name"] == owner.last_name
```

В тестах нет сырых `requests` и SQL: для этого существуют слои API и DB.

## Архитектура

```text
Pytest
  → OwnerApi / PetApi / VisitApi        знают endpoints и операции ресурса
  → BaseApiClient                       HTTP transport
  → Spring PetClinic REST               тестируемое приложение (в Docker)
  → PostgreSQL / MySQL
  → DatabaseClient                      подключение, выполнение SQL, fetch
  → OwnerRepository / PetRepository / VisitRepository   SQL конкретных сущностей
```

| Слой | Папка | Ответственность |
|---|---|---|
| Конфигурация | `config/` | Настройки из `.env` (pydantic-settings). Ничего внутреннего не импортирует |
| API Objects | `api/` | Операции над ресурсом. `BaseApiClient` знает только HTTP и прикладывает запрос/ответ к Allure |
| DB | `db/` | `DatabaseClient` — транспорт; репозитории — параметризованный SQL по сущностям |
| Модели | `models/` | Pydantic-модели запросов (camelCase в API, snake_case в Python) |
| Фабрики | `factories/` | Валидные тестовые данные на Faker с возможностью override |
| Тесты | `tests/` | `owners`, `pets`, `visits`, `integration` |
| Fixtures | `conftest.py` | Lifecycle: подготовка → тест → cleanup |

Принципы:
- `api` не выполняет SQL, `db` не выполняет HTTP.
- Весь SQL параметризованный (`%s`), без f-string и конкатенации.
- ORM для DB-проверок не используется: цель — показать работу с SQL напрямую.
- Тесты независимы, порядок запуска не важен. Сквозной сценарий владелец → питомец → визит вынесен в отдельные integration-тесты.
- Данные, созданные тестом, удаляются по id в teardown. Порядок удаления (визиты → питомцы → владельцы) задаётся цепочкой зависимостей fixtures, чтобы не нарушать внешние ключи.

## Быстрый старт

Нужны Python 3.13 и Docker.

```bash
# 1. Настройки
cp .env.example .env

# 2. Стенд: PetClinic + база
docker compose up -d

# 3. Зависимости
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install --group dev

# 4. Тесты
pytest
```

PetClinic стартует около 30 секунд после того, как база стала healthy. Проверить готовность:

```bash
curl http://localhost:9966/petclinic/api/owners
```

Остановить стенд и удалить данные:

```bash
docker compose --profile "*" down -v
```

## Настройки

Всё задаётся через `.env`. Файл `.env` не коммитится, `.env.example` — коммитится.

| Переменная | Значение по умолчанию | Описание |
|---|---|---|
| `API_BASE_URL` | `http://localhost:9966/petclinic` | Адрес PetClinic |
| `DB_ENGINE` | `postgres` | `postgres` или `mysql`. Выбирает и драйвер тестов, и стенд Docker Compose |
| `COMPOSE_PROFILES` | `${DB_ENGINE}` | Какие сервисы поднимает Compose |
| `DB_HOST` | `localhost` | |
| `DB_PORT` | `5432` | 5432 для postgres, 3306 для mysql |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | `petclinic` | |

## PostgreSQL и MySQL

Тесты, репозитории и фабрики одинаковы для обеих баз. Различие скрыто в одном месте — `DatabaseClient` выбирает драйвер (`psycopg` или `PyMySQL`) по `DB_ENGINE`. Docker Compose поднимает нужную пару сервисов через профили.

Переключение базы:

```bash
docker compose --profile "*" down -v
# в .env: DB_ENGINE=mysql и DB_PORT=3306
docker compose up -d
pytest
```

На обеих базах результат одинаковый: 55 passed, 6 xfailed.

## Запуск тестов

```bash
pytest                         # весь набор
pytest -m smoke                # критичные проверки
pytest -m positive             # валидные сценарии
pytest -m negative             # некорректный ввод и обработка ошибок
pytest -m db                   # проверки состояния базы
pytest -m integration          # сквозные сценарии
pytest -m "not slow"
pytest tests/owners            # один ресурс
```

Маркеры: `smoke`, `positive`, `negative`, `integration`, `db`, `slow`. Запуск идёт с `--strict-markers`, неизвестный маркер — ошибка.

Состав набора: 61 тест (owners — 21, pets — 19, visits — 17, integration — 4); 55 проходят, 6 помечены как xfail (см. ниже).

## Расхождения PetClinic и xfail

PetClinic не всегда ведёт себя так, как ожидается от REST API. Такие расхождения не маскируются: тест формулирует **правильное** ожидание и помечается `xfail(strict=True)` с описанием бага. Если приложение починят, тест станет XPASS и упадёт (`strict`), напоминая снять метку. Поведение одинаково на PostgreSQL и MySQL.

| Тест | Ожидание | Фактически |
|---|---|---|
| Создание владельца с некорректным телефоном | 400 | 500 |
| Создание питомца с пустым именем | 400 | 500 |
| Создание питомца с неверным форматом даты | 400 | 500 |
| Создание визита с неверным форматом даты | 400 | 500 |
| Создание визита для несуществующего владельца | 404 | 201, визит создаётся |
| Удаление владельца, у которого есть питомцы | 409 | 404 |

## Allure-отчёт

Результаты пишутся в `allure-results/` при каждом запуске `pytest` (папка очищается автоматически). В отчёте:
- каждый HTTP-вызов — отдельный шаг (`POST /api/owners`) с вложениями **Request** и **Response**;
- вкладка Environment: URL, движок и параметры БД (пароль не включается);
- вкладка Behaviors: epic `PetClinic REST` и feature по папке теста (`Owners`, `Pets`, `Visits`, `Integration`).

Чтобы посмотреть отчёт локально, нужен [Allure CLI](https://allurereport.org/docs/install/):

```bash
allure serve allure-results
```

## CI

GitHub Actions (`.github/workflows/api-db-tests.yml`):

1. **Code quality** — `ruff check` и `ruff format --check`.
2. **Tests** — matrix `postgres` и `mysql`: создаётся `.env`, поднимается стенд в Docker, ожидается готовность PetClinic, запускается `pytest`. Результаты Allure сохраняются артефактом `allure-results-<engine>`, при падении печатаются логи стенда.
3. **Publish Allure report** — отчёт по PostgreSQL публикуется на GitHub Pages (только из `main`) с сохранением истории прогонов, а также сохраняется артефактом.

Отчёт: https://sslonikq.github.io/spring-petclinic-api-sql-framework/

## Качество кода

```bash
ruff check .
ruff format --check .
```

## Структура проекта

```text
config/                 настройки из .env
api/                    BaseApiClient, OwnerApi, PetApi, VisitApi
db/
  client.py             DatabaseClient (PostgreSQL и MySQL)
  repositories/         SQL по сущностям
models/                 Pydantic-модели
factories/              Faker-фабрики
tests/
  owners/               CRUD, negative, DB validation
  pets/
  visits/
  integration/          сквозной сценарий владелец → питомец → визит
conftest.py             fixtures, Allure environment и разметка
docker-compose.yml      PetClinic + PostgreSQL / MySQL (профили)
.env.example            безопасная конфигурация
pyproject.toml          зависимости, pytest, ruff
```
