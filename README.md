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

**Триггеры:** push в ветку **`main`** или ручной запуск (**Actions → Run workflow**, ветка **main**).

**Job `build`**

1. Checkout репозитория  
2. Docker Buildx  
3. Вход в **GHCR** (`ghcr.io`) под `GITHUB_TOKEN`  
4. Сборка и **push** образа с тегом **`latest`**

После успешного прогона образ доступен в пакетах репозитория на GitHub (**Packages**), имя вида `ghcr.io/<владелец>/<репозиторий>:latest` (реестр приводит имя к нижнему регистру).

### Автодеплой на VPS по SSH

При каждом **push в `main`** (и при ручном **Run workflow** для ветки **main**) после успешной сборки образа запускается job **deploy**: подключение по SSH, `docker pull` из **GHCR** и запуск контейнера.

**Что нужно один раз:**

1. На VPS установлен **Docker**, пользователь из секрета `USERNAME` может выполнять `docker` (**root** или пользователь в группе `docker`: `sudo usermod -aG docker ИМЯ && newgrp docker`).
2. Открыты порты **22** (SSH) и **8000** (приложение) — локально `ufw`, у хостера — security group / firewall.
3. В репозитории GitHub: **Settings → Secrets and variables → Actions → Secrets** (имена должны совпадать с workflow):

| Секрет | Содержимое |
|--------|------------|
| `HOST` | IP или домен VPS |
| `USERNAME` | пользователь SSH (`root` или другой) |
| `SSH_KEY` | **полный** приватный ключ (включая строки `BEGIN` / `END`) |
| `PORT` | опционально; если не задан — используется **22** |

Без этих секретов job **deploy** завершится ошибкой; job **build** и публикация образа в GHCR всё равно выполняются.

На сервере контейнер называется **`vpe04-time-api`**, слушает **8000** на хосте (`-p 8000:8000`). Проверка: `http://<IP>:8000/docs`

Повторный деплой без нового коммита: **Actions → Build and Deploy → Run workflow** (ветка **main**).

### Проверка деплоя на реальном VPS

Сделайте по порядку.

**1. Сервер (Ubuntu)** — по SSH зайдите под тем пользователем, что укажете в `USERNAME` (часто `root`).

```bash
# Docker установлен?
docker --version
```

Если команды нет, для Ubuntu 24 см. [официальную установку Docker Engine](https://docs.docker.com/engine/install/ubuntu/) или кратко:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${VERSION_CODENAME:-stable}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**2. Доступ по SSH-ключу** — в секрет `SSH_KEY` кладётся **приватный** ключ (целиком, с `BEGIN` / `END`). На сервере в `~/.ssh/authorized_keys` у этого пользователя должна быть строка из **публичного** ключа (`*.pub`), соответствующего этому приватному. Пароль без ключа для `appleboy/ssh-action` не подойдёт.

Проверка с вашего ПК (подставьте ключ и адрес):

```bash
ssh -i C:\Users\Eduard\.ssh\id_rsa_work -p 22 USER@IP "docker --version"
```

**3. Файрвол** — снаружи должен быть доступен порт **8000** (и **22** для GitHub).

```bash
sudo ufw status
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp
sudo ufw enable   # если ещё не включён
```

У хостера в панели иногда отдельно открывают «Security Group» / входящие правила — добавьте **TCP 8000** откуда угодно или с вашего IP.

**4. GitHub** — в вашем репозитории: **Settings → Secrets and variables → Actions**:

| Имя | Значение |
|-----|----------|
| `HOST` | IP или домен VPS |
| `USERNAME` | пользователь SSH (`root` или другой) |
| `SSH_KEY` | приватный ключ (одна многострочная секретная запись) |
| `PORT` | опционально, если SSH не на 22 |

**5. Запуск** — сделайте **push в `main`** или **Actions → Build and Deploy → Run workflow** (ветка **main**).

**6. Проверка результата** — в логе job **deploy** должны быть `docker pull` и `docker run` без ошибок. В браузере: `http://<IP>:8000/` и `http://<IP>:8000/docs`.

**Типичные ошибки**

| Симптом | Что проверить |
|---------|----------------|
| `missing server host` / SSH не коннектится | `HOST`, `PORT`, ключ в Secrets, `authorized_keys` на сервере |
| `docker: command not found` | Установить Docker на VPS |
| Ошибка при `docker pull` / `denied` | Образ в GHCR после успешного **build**; логин в скрипте использует `GITHUB_TOKEN` от того же workflow |
| Сайт не открывается по `:8000` | `ufw`/панель хостера, контейнер `docker ps` на сервере |
| `permission denied` при `docker` не под root | Добавить пользователя в группу `docker` или использовать `USERNAME=root` |

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
