# Lesson VPe04 — Time Server API (CI/CD)

Учебный проект по модулю **«Серверное развертывание»**: **FastAPI**, сборка **Docker**-образа, публикация в **GitHub Container Registry (GHCR)** и **автодеплой на VPS по SSH** через **GitHub Actions** при каждом push в ветку **`main`**.

Репозиторий: [Shch2295404/test-AutoDeploy](https://github.com/Shch2295404/test-AutoDeploy).

## Возможности

- REST API: время и дата в **UTC** (`/time`, `/date`, `/datetime`)
- Перевод момента из **UTC** в локальное время по **IANA**-часовому поясу (`/convert`)
- **Swagger UI**: `/docs`
- **CI/CD**: при push в **`main`** — сборка образа → push в GHCR → по SSH обновление контейнера на сервере

## Требования

- Python 3.12+ (локально)
- [Docker](https://docs.docker.com/get-docker/) — для запуска в контейнере

## Быстрый старт (локально)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux / macOS

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Откройте: `http://127.0.0.1:8000/docs`

## Docker (локально)

```bash
docker build -t time-server-api .
docker run --rm -p 8000:8000 time-server-api
```

## Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Приветствие |
| GET | `/time` | Текущее время UTC (ISO 8601) |
| GET | `/date` | Текущая дата UTC |
| GET | `/datetime` | Дата и время UTC |
| GET | `/convert` | UTC → время в выбранной зоне (см. ниже) |

### `/convert`

Параметры запроса:

| Параметр | Обязательный | Описание |
|----------|----------------|----------|
| `tz` | да | IANA-имя зоны: `Europe/Moscow`, `Asia/Yekaterinburg`, `UTC`, … |
| `utc_iso` | нет | Момент в UTC (ISO 8601); если не указан — текущее время сервера в UTC |

Ответ: `timezone`, `utc_iso`, `local_iso`, `utc_offset` (например `+03:00`). Неверная зона — **400**.

Примеры после деплоя (подставьте IP вашего VPS):

```http
GET http://<VPS_IP>:8000/convert?tz=Europe/Moscow
GET http://<VPS_IP>:8000/convert?tz=Asia/Yekaterinburg&utc_iso=2026-05-13T12:00:00Z
```

## GitHub Actions

Файл: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

**Триггеры:** push в **`main`**, ручной запуск (**Actions → Build and Deploy → Run workflow**, ветка **main**).

| Job | Действие |
|-----|----------|
| **build** | Checkout → Docker Buildx → вход в GHCR → сборка и push образа с тегом **`latest`** |
| **deploy** | После успешного **build**: SSH на VPS → `docker login` ghcr.io → `pull` → перезапуск контейнера **`vpe04-time-api`** (`-p 8000:8000`) |

Образ в реестре: `ghcr.io/<владелец>/<репозиторий>:latest` (имя приводится к нижнему регистру).

### Секреты для деплоя (Settings → Secrets and variables → Actions)

Без них job **deploy** падает; **build** и образ в GHCR всё равно выполняются.

| Секрет | Содержимое |
|--------|------------|
| `HOST` | IP или домен VPS |
| `USERNAME` | пользователь SSH (`root` или другой с правом `docker`) |
| `SSH_KEY` | полный **приватный** ключ (`BEGIN` … `END`) |
| `PORT` | опционально; если нет — используется **22** |

На VPS: установлен **Docker**, открыты **22** (SSH) и **8000** (HTTP приложения); вход по SSH для Actions — **только по ключу** (публичный ключ в `~/.ssh/authorized_keys`). Не root: пользователь в группе `docker` (`sudo usermod -aG docker <user>`).

Краткая установка Docker на Ubuntu: [Docker Engine (Ubuntu)](https://docs.docker.com/engine/install/ubuntu/). Файрвол: `ufw allow 22,8000/tcp` и правила у хостера (security group).

### Проверка после деплоя

1. **Actions** — workflow **Build and Deploy** зелёный, в **deploy** есть успешные `docker pull` / `docker run`.
2. Браузер: `http://<VPS_IP>:8000/docs` — открывается Swagger (**Time Server API**).
3. Опционально: `http://<VPS_IP>:8000/convert?tz=Europe/Moscow` — JSON с полями `utc_iso`, `local_iso`.

Повторный прогон без коммита: **Run workflow** на ветке **main**.

### Типичные ошибки

| Симптом | Что проверить |
|---------|----------------|
| SSH / `missing server host` | `HOST`, `PORT`, `SSH_KEY`, ключ в `authorized_keys` на сервере |
| `docker: command not found` на VPS | Установить Docker |
| Ошибка `docker pull` / `denied` | Успешный **build**; образ в GHCR; токен в workflow для `docker login` |
| Не открывается `:8000` | `ufw`, firewall хостера; `docker ps` на сервере — контейнер `vpe04-time-api` |
| `permission denied` для docker | Пользователь в группе `docker` или деплой под `root` |

## Структура репозитория

```
Lesson_VPe04/
├── main.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .github/workflows/deploy.yml   # build → GHCR → SSH deploy
└── README.md
```

## Связь с уроком

Кейс **VPe04** курса «Профессия — вайб-кодер»: **CI/CD**, **GitHub Actions**, **Docker**, **GHCR**, **Secrets**, деплой по **SSH**, модель веток (**GitFlow** / работа с **`main`**).
