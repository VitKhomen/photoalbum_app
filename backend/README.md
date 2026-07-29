# Photo Album — Backend

FastAPI-бекенд для сайту-фотоальбому. Публічний перегляд альбомів + фото,
завантаження та керування — тільки через адмінку (JWT, один суперюзер).

## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM
- **Alembic** — міграції БД
- **PostgreSQL** — база даних
- **python-decouple** — конфіг з `.env`
- **dj-database-url** — парсинг рядка підключення до БД
- **Cloudflare R2** (через `boto3`, S3-сумісний API) — сховище фото
- **python-jose + passlib** — JWT-авторизація адміна

## Структура

```
backend/
  app/
    main.py            # точка входу FastAPI
    config.py           # читання .env (decouple)
    database.py         # engine/session, парсинг DATABASE_URL (dj-database-url)
    models.py            # Album, Photo (SQLAlchemy)
    schemas.py           # Pydantic-схеми
    security.py          # JWT + bcrypt
    dependencies.py      # get_current_admin (захист адмін-роутів)
    storage.py            # завантаження/видалення файлів у Cloudflare R2
    crud.py                # робота з БД
    routers/
      public.py            # GET /api/albums, GET /api/albums/{slug}
      admin.py              # POST /api/admin/login + CRUD (захищено JWT)
  migrations/            # Alembic
  scripts/hash_password.py  # генерація хешу пароля адміна
  requirements.txt
  .env.example
```

## Модель даних

- **Album**: `id, title, slug, description, order, cover_photo_id, created_at, updated_at`
- **Photo**: `id, album_id, file_key, url, width, height, order, created_at`

`order` в обох моделях відповідає за чергу показу (альбоми по черзі на головній,
фото по черзі всередині альбому/лайтбоксу).

## Запуск локально

1. Створити віртуальне середовище і встановити залежності:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Скопіювати `.env.example` в `.env` і заповнити:

   ```bash
   cp .env.example .env
   ```

   - `DATABASE_URL` — рядок підключення до Postgres
   - `SECRET_KEY` — будь-який довгий випадковий рядок
   - `R2_*` — дані бакета Cloudflare R2 (Account ID, Access Key, Secret Key, назва бакета)
   - `R2_PUBLIC_URL` — публічний домен бакета (r2.dev або кастомний домен)

3. Згенерувати хеш пароля адміна та вписати в `.env` (`ADMIN_PASSWORD_HASH`):

   ```bash
   python scripts/hash_password.py "мій_пароль"
   ```

4. Створити базу в Postgres (наприклад `photoalbum`), потім застосувати міграції:

   ```bash
   alembic revision --autogenerate -m "init"
   alembic upgrade head
   ```

5. Запустити сервер розробки:

   ```bash
   uvicorn app.main:app --reload
   ```

   Swagger-документація: http://localhost:8000/docs

## Основні ендпоінти

**Публічні:**
- `GET /api/albums` — список альбомів (по черзі, з обкладинкою й кількістю фото)
- `GET /api/albums/{slug}` — альбом з усіма фото

**Адмінка (потрібен `Authorization: Bearer <token>`):**
- `POST /api/admin/login` — логін (`username`, `password`) → `access_token`
- `POST /api/admin/albums` — створити альбом
- `PUT /api/admin/albums/{id}` — оновити альбом (в т.ч. обкладинку)
- `DELETE /api/admin/albums/{id}` — видалити альбом (і всі фото з R2)
- `POST /api/admin/albums/{id}/photos` — завантажити фото (multipart/form-data, поле `file`)
- `DELETE /api/admin/photos/{id}` — видалити фото
- `PUT /api/admin/albums/{id}/photos/reorder` — змінити порядок фото

## Налаштування Cloudflare R2

1. Створити бакет в Cloudflare Dashboard → R2.
2. Увімкнути публічний доступ (r2.dev subdomain) або підʼєднати власний домен.
3. Створити API-токен (R2 → Manage API Tokens) з правами читання/запису —
   отримаєте `Access Key ID` і `Secret Access Key`.
4. `R2_ACCOUNT_ID` — знаходиться в Cloudflare Dashboard (правий сайдбар акаунта).

## Що далі (не входить у цей скоуп)

- Фронтенд (Vue) — окрема папка `frontend/`, буде зроблено окремим кроком.
- Генерація thumbnail'ів (зараз віддається оригінал; можна додати resize
  через Pillow при завантаженні, якщо потрібно оптимізувати вагу на мобільних).
