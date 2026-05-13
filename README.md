# Lesson VPe04 — Time Server API (CI/CD)

Учебный проект по модулю **«Серверное развертывание»**: простой бэкенд на **FastAPI**, сборка **Docker**-образа и публикация в **GitHub Container Registry (GHCR)** через **GitHub Actions**; опционально — деплой на VPS по **SSH** (как в кейсе урока).

## Возможности

- REST API с текущим временем и датой в **UTC**
- Swagger UI по адресу `/docs`
- Автоматическая сборка и пуш образа при **push в ветку `main`**

## Требования

- Python 3.12+ (локально достаточно совместимой версии с зависимостями)
- [Docker](https://docs.docker.com/get-docker/) — для локального запуска в контейнере

## Быстрый старт (локально)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux / macOS

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Откройте в браузере: `http://127.0.0.1:8000/docs`

## Docker (локально)

```bash
docker build -t time-server-api .
docker run --rm -p 8000:8000 time-server-api
```

Проверка: `http://127.0.0.1:8000/` и `http://127.0.0.1:8000/docs`

## Эндпоинты

| Метод | Путь        | Описание                          |
|-------|-------------|-----------------------------------|
| GET   | `/`         | Приветственное сообщение        |
| GET   | `/time`     | Текущее время UTC (ISO 8601)    |
| GET   | `/date`     | Текущая дата UTC                |
| GET   | `/datetime` | Дата и время UTC                |

## GitHub Actions

Файл: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)

**Триггер:** push в ветку **`main`**.

**Job `build`**

1. Checkout репозитория  
2. Docker Buildx  
3. Вход в **GHCR** (`ghcr.io`) под `GITHUB_TOKEN`  
4. Сборка и **push** образа с тегом **`latest`**

После успешного прогона образ доступен в пакетах репозитория на GitHub (**Packages**), имя вида `ghcr.io/<владелец>/<репозиторий>:latest` (реестр приводит имя к нижнему регистру).

### Опциональный деплой на сервер (SSH)

Чтобы после сборки автоматически обновлялся контейнер на VPS:

1. На сервере установлен **Docker**, открыт SSH (часто порт **22**).
2. В репозитории: **Settings → Secrets and variables → Actions → Secrets**:
   - `HOST` — IP или hostname сервера  
   - `USERNAME` — пользователь SSH (например, `root`)  
   - `SSH_KEY` — **приватный** ключ в одну строку (как в уроке)  
   - `PORT` — порт SSH (необязательно; если секрета нет, используется **22**)
3. В **Variables** того же раздела создайте переменную **`ENABLE_SSH_DEPLOY`** со значением **`true`**.  
   Пока переменная не задана или не равна `true`, job **deploy** пропускается — сборка в GHCR всё равно выполняется.

На сервере контейнер запускается с именем **`vpe04-time-api`**, порт приложения **8000** проброшен на хост (`-p 8000:8000`). Проверка: `http://<IP_сервера>:8000/docs`

## Структура репозитория

```
Lesson_VPe04/
├── main.py                 # FastAPI-приложение
├── requirements.txt      # Зависимости Python
├── Dockerfile              # Сборка образа приложения
├── .dockerignore
├── .github/
│   └── workflows/
│       └── deploy.yml      # CI: build + push в GHCR; опционально SSH deploy
└── README.md
```

## Связь с уроком

Материал опирается на темы **CI/CD**, **GitHub Actions**, **Docker**, **GHCR**, **Secrets** и (по желанию) деплой по SSH — как в кейсе **VPe04** курса «Профессия — вайб-кодер».
