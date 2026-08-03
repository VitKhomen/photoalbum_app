# Тестові запити до API (Photo Album)

Приклади на `curl` для ручної перевірки всіх ендпоінтів. Заміни `BASE_URL`
на свій (локально: `http://localhost:8000`).

```bash
export BASE_URL="http://localhost:8000"
```

Порядок тестування нижче саме такий, у якому має сенс запускати (спочатку
логін → створення альбому → завантаження фото → ... → видалення).

---

## 0. Health-check

```bash
curl -s "$BASE_URL/api/health"
```

Очікувано: `{"status":"ok"}`

---

## 1. Публічні ендпоінти (без токена)

### 1.1. Список альбомів

```bash
curl -s "$BASE_URL/api/albums" | python3 -m json.tool
```

Очікувано (поки альбомів нема): `[]`

### 1.2. Один альбом за slug

```bash
curl -s "$BASE_URL/api/albums/vidpustka-2026" | python3 -m json.tool
```

Очікувано, якщо такого slug нема: `404 {"detail":"Альбом не знайдено"}`

---

## 2. Логін адміна

```bash
curl -s -X POST "$BASE_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ТВІЙ_ПАРОЛЬ"}' \
  | python3 -m json.tool
```

Очікувано: `{"access_token": "...", "token_type": "bearer"}`

Збережи токен у змінну для наступних запитів:

```bash
export TOKEN=$(curl -s -X POST "$BASE_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ТВІЙ_ПАРОЛЬ"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

echo $TOKEN
```

### Негативний тест — неправильний пароль

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST "$BASE_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "неправильний"}'
```

Очікувано: `401`

---

## 3. Адмінка — Альбоми (потрібен `$TOKEN`)

### 3.1. Створити альбом

```bash
curl -s -X POST "$BASE_URL/api/admin/albums" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Відпустка 2026", "description": "Море і сонце", "order": 1}' \
  | python3 -m json.tool
```

Збережи `id` з відповіді:

```bash
export ALBUM_ID=1
export SLUG=vidpustka-2026   # slug з відповіді вище
```

### Негативний тест — без токена

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST "$BASE_URL/api/admin/albums" \
  -H "Content-Type: application/json" \
  -d '{"title": "Без токена", "order": 1}'
```

Очікувано: `401`

### 3.2. Оновити альбом

```bash
curl -s -X PUT "$BASE_URL/api/admin/albums/$ALBUM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Відпустка 2026 (оновлено)", "order": 2}' \
  | python3 -m json.tool
```

### 3.3. Видалити альбом

⚠️ Каскадно видаляє всі фото альбому (і в базі, і в R2). Запускай в кінці.

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X DELETE \
  "$BASE_URL/api/admin/albums/$ALBUM_ID" \
  -H "Authorization: Bearer $TOKEN"
```

Очікувано: `204`

---

## 4. Адмінка — Фото (потрібен `$TOKEN` і `$ALBUM_ID`)

### 4.1. Завантажити фото

```bash
curl -s -X POST "$BASE_URL/api/admin/albums/$ALBUM_ID/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/шлях/до/фото.jpg;type=image/jpeg" \
  | python3 -m json.tool
```

Збережи `id` з відповіді:

```bash
export PHOTO_ID=1
```

Негативний тест — заборонений тип файлу (наприклад `.txt`):

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
  "$BASE_URL/api/admin/albums/$ALBUM_ID/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/шлях/до/файлу.txt;type=text/plain"
```

Очікувано: `400`

### 4.2. Змінити порядок фото в альбомі

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X PUT \
  "$BASE_URL/api/admin/albums/$ALBUM_ID/photos/reorder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"id": 1, "order": 2}, {"id": 2, "order": 1}]}'
```

Очікувано: `204`

### 4.3. Видалити фото

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X DELETE \
  "$BASE_URL/api/admin/photos/$PHOTO_ID" \
  -H "Authorization: Bearer $TOKEN"
```

Очікувано: `204`

---

## 5. Перевірка публічно після дій адміна

```bash
# альбом тепер має з'явитись у списку і мати фото
curl -s "$BASE_URL/api/albums" | python3 -m json.tool
curl -s "$BASE_URL/api/albums/$SLUG" | python3 -m json.tool
```

---

## Швидкий скрипт для повного циклу (bash)

Копіюй і виконуй по черзі — пройде повний happy-path сценарій.

```bash
export BASE_URL="http://localhost:8000"
export PASSWORD="ТВІЙ_ПАРОЛЬ"

export TOKEN=$(curl -s -X POST "$BASE_URL/api/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"admin\", \"password\": \"$PASSWORD\"}" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

echo "Токен отримано: ${TOKEN:0:20}..."

ALBUM=$(curl -s -X POST "$BASE_URL/api/admin/albums" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title": "Тест з requests.md", "order": 1}')
echo "$ALBUM" | python3 -m json.tool

ALBUM_ID=$(echo "$ALBUM" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")
echo "ALBUM_ID=$ALBUM_ID"

curl -s "$BASE_URL/api/albums" | python3 -m json.tool

curl -s -o /dev/null -w "видалення альбому: %{http_code}\n" -X DELETE \
  "$BASE_URL/api/admin/albums/$ALBUM_ID" -H "Authorization: Bearer $TOKEN"
```

---

## Альтернатива: Swagger UI

Все те саме можна робити руками через автогенеровану документацію,
без curl — зручно для швидкої ручної перевірки й для завантаження фото
(там є нормальна форма для файлів):

```
$BASE_URL/docs
```

Кнопка **Authorize** зверху приймає JWT-токен з `/api/admin/login`
(вводити як `Bearer <токен>` або просто `<токен>`, залежно від версії Swagger).
