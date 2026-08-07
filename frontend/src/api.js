import { useAuth } from "./stores/auth.js";


// Базовий URL бекенду. Для локальної розробки лежить у .env (VITE_API_BASE_URL),
// на проді підставляється при білді.
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Помилка запиту: ${res.status}`);
  }
  return res.json();
}

/** Список усіх альбомів по черзі (для головної сторінки). */
export function fetchAlbums() {
  return request("/api/albums");
}

/** Один альбом з усіма фото за slug. */
export function fetchAlbum(slug) {
  return request(`/api/albums/${slug}`);
}

/** Логін адміна - повертає JWT access_token. */
export async function loginRequest(username, password) {
  const res = await fetch(`${API_BASE}/api/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Невірний логін або пароль");
  }
  return res.json(); // { access_token, token_type }
}



function authHeaders() {
  const { token } = useAuth();
  return { Authorization: `Bearer ${token.value}` };
}

async function adminRequest(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Помилка запиту: ${res.status}`);
  }
  // 204 No Content - тіла нема, парсити нема що
  if (res.status === 204) return null;
  return res.json();
}

/** Створити альбом. */
export function createAlbum({ title, description, order }) {
  return adminRequest("/api/admin/albums", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description, order }),
  });
}

/** Оновити альбом (title/description/order/slug/cover_photo_id - будь-які поля частково). */
export function updateAlbum(albumId, data) {
  return adminRequest(`/api/admin/albums/${albumId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

/** Видалити альбом (каскадно видаляє й фото). */
export function deleteAlbum(albumId) {
  return adminRequest(`/api/admin/albums/${albumId}`, { method: "DELETE" });
}

/** Завантажити фото в альбом (multipart/form-data). */
export function uploadPhoto(albumId, file) {
  const formData = new FormData();
  formData.append("file", file);
  return adminRequest(`/api/admin/albums/${albumId}/photos`, {
    method: "POST",
    body: formData, // Content-Type НЕ виставляємо вручну - браузер сам додасть з boundary
  });
}

export function uploadPhotoWithProgress(albumId, file, onProgress) {
  return new Promise((resolve, reject) => {
    const { token } = useAuth();
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE}/api/admin/albums/${albumId}/photos`);
    xhr.setRequestHeader("Authorization", `Bearer ${token.value}`);

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    });

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(xhr.responseText ? JSON.parse(xhr.responseText) : null);
      } else {
        let detail = `Помилка запиту: ${xhr.status}`;
        try {
          detail = JSON.parse(xhr.responseText).detail || detail;
        } catch {
          /* тіло не JSON - лишаємо дефолтний текст помилки */
        }
        reject(new Error(detail));
      }
    };
    xhr.onerror = () => reject(new Error("Мережева помилка під час завантаження"));

    const formData = new FormData();
    formData.append("file", file);
    xhr.send(formData);
  });
}

/** Видалити фото. */
export function deletePhoto(photoId) {
  return adminRequest(`/api/admin/photos/${photoId}`, { method: "DELETE" });
}

/** Змінити порядок фото в альбомі. items: [{id, order}, ...] */
export function reorderPhotos(albumId, items) {
  return adminRequest(`/api/admin/albums/${albumId}/photos/reorder`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items }),
  });
}