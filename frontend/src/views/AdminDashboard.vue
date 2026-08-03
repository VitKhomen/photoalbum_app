<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "../stores/auth.js";
import {
  fetchAlbums,
  fetchAlbum,
  createAlbum,
  updateAlbum,
  deleteAlbum,
  uploadPhoto,
  deletePhoto,
  reorderPhotos,
} from "../api.js";

const router = useRouter();
const { logout } = useAuth();

const albums = ref([]);
const isLoadingAlbums = ref(true);
const listError = ref(null);

const selectedAlbum = ref(null); // повна версія (з photos) обраного альбому
const isLoadingDetail = ref(false);

const newTitle = ref("");
const newDescription = ref("");
const isCreating = ref(false);
const createError = ref(null);

const editTitle = ref("");
const editDescription = ref("");
const isSavingEdit = ref(false);

const uploadError = ref(null);
const isUploading = ref(false);
const fileInput = ref(null);

async function loadAlbums() {
  isLoadingAlbums.value = true;
  listError.value = null;
  try {
    albums.value = await fetchAlbums();
  } catch (e) {
    listError.value = e.message;
  } finally {
    isLoadingAlbums.value = false;
  }
}

async function selectAlbum(album) {
  isLoadingDetail.value = true;
  uploadError.value = null;
  try {
    selectedAlbum.value = await fetchAlbum(album.slug);
    editTitle.value = selectedAlbum.value.title;
    editDescription.value = selectedAlbum.value.description || "";
  } finally {
    isLoadingDetail.value = false;
  }
}

async function refreshSelected() {
  if (!selectedAlbum.value) return;
  selectedAlbum.value = await fetchAlbum(selectedAlbum.value.slug);
}

async function handleCreateAlbum() {
  if (!newTitle.value.trim()) return;
  isCreating.value = true;
  createError.value = null;
  try {
    await createAlbum({
      title: newTitle.value.trim(),
      description: newDescription.value.trim() || null,
      order: albums.value.length + 1,
    });
    newTitle.value = "";
    newDescription.value = "";
    await loadAlbums();
  } catch (e) {
    createError.value = e.message;
  } finally {
    isCreating.value = false;
  }
}

async function handleDeleteAlbum(album) {
  if (!confirm(`Видалити альбом "${album.title}" разом з усіма фото? Це незворотно.`)) return;
  await deleteAlbum(album.id);
  if (selectedAlbum.value?.id === album.id) selectedAlbum.value = null;
  await loadAlbums();
}

async function handleSaveEdit() {
  if (!selectedAlbum.value) return;
  isSavingEdit.value = true;
  try {
    await updateAlbum(selectedAlbum.value.id, {
      title: editTitle.value.trim(),
      description: editDescription.value.trim() || null,
    });
    await refreshSelected();
    await loadAlbums();
  } finally {
    isSavingEdit.value = false;
  }
}

async function handleFileChange(e) {
  const files = Array.from(e.target.files || []);
  if (files.length === 0 || !selectedAlbum.value) return;

  isUploading.value = true;
  uploadError.value = null;

  const failed = [];

  for (const file of files) {
    try {
      await uploadPhoto(selectedAlbum.value.id, file);
    } catch (err) {
      failed.push(`${file.name}: ${err.message}`);
    }
  }

  await refreshSelected();
  await loadAlbums();

  if (failed.length > 0) {
    uploadError.value = `Не завантажено ${failed.length} з ${files.length}: ${failed.join("; ")}`;
  }

  isUploading.value = false;
  if (fileInput.value) fileInput.value.value = "";
}

async function handleDeletePhoto(photo) {
  if (!confirm("Видалити це фото?")) return;
  await deletePhoto(photo.id);
  await refreshSelected();
  await loadAlbums();
}

async function handleSetCover(photo) {
  await updateAlbum(selectedAlbum.value.id, { cover_photo_id: photo.id });
  await refreshSelected();
  await loadAlbums();
}

async function movePhoto(photo, direction) {
  const photos = selectedAlbum.value.photos;
  const i = photos.findIndex((p) => p.id === photo.id);
  const j = i + direction;
  if (j < 0 || j >= photos.length) return;

  const reordered = [...photos];
  [reordered[i], reordered[j]] = [reordered[j], reordered[i]];
  const items = reordered.map((p, idx) => ({ id: p.id, order: idx + 1 }));

  await reorderPhotos(selectedAlbum.value.id, items);
  await refreshSelected();
}

function handleLogout() {
  logout();
  router.push("/admin/login");
}

onMounted(loadAlbums);
</script>

<template>
  <div class="dashboard">
    <header class="dashboard__header">
      <h1 class="dashboard__title">Адмінка</h1>
      <button class="btn btn--ghost" @click="handleLogout">Вийти</button>
    </header>

    <div class="dashboard__body">
      <aside class="dashboard__sidebar">
        <form class="new-album" @submit.prevent="handleCreateAlbum">
          <input
            v-model="newTitle"
            type="text"
            placeholder="Назва нового альбому"
            required
          />
          <textarea
            v-model="newDescription"
            placeholder="Опис (необов'язково)"
            rows="2"
          />
          <button class="btn" type="submit" :disabled="isCreating">
            {{ isCreating ? "Створюємо..." : "+ Новий альбом" }}
          </button>
          <p v-if="createError" class="error-text">{{ createError }}</p>
        </form>

        <div v-if="isLoadingAlbums" class="muted">Завантаження...</div>
        <div v-else-if="listError" class="error-text">{{ listError }}</div>
        <div v-else-if="albums.length === 0" class="muted">Альбомів поки немає</div>

        <ul v-else class="album-list">
          <li
            v-for="album in albums"
            :key="album.id"
            class="album-list__item"
            :class="{ 'album-list__item--active': selectedAlbum?.id === album.id }"
          >
            <button class="album-list__select" @click="selectAlbum(album)">
              <span class="album-list__title">{{ album.title }}</span>
              <span class="album-list__meta">{{ album.photos_count }} фото</span>
            </button>
            <button
              class="album-list__delete"
              @click="handleDeleteAlbum(album)"
              aria-label="Видалити альбом"
            >
              ×
            </button>
          </li>
        </ul>
      </aside>

      <section class="dashboard__detail">
        <div v-if="isLoadingDetail" class="muted">Завантаження альбому...</div>

        <div v-else-if="!selectedAlbum" class="muted muted--center">
          Обери альбом зліва, щоб редагувати
        </div>

        <div v-else class="album-editor">
          <form class="album-editor__meta" @submit.prevent="handleSaveEdit">
            <input v-model="editTitle" type="text" placeholder="Назва" required />
            <textarea v-model="editDescription" placeholder="Опис" rows="2" />
            <button class="btn" type="submit" :disabled="isSavingEdit">
              {{ isSavingEdit ? "Зберігаємо..." : "Зберегти" }}
            </button>
          </form>

          <div class="album-editor__upload">
            <label class="btn">
              {{ isUploading ? "Завантажуємо..." : "+ Додати фото" }}
              <input
                ref="fileInput"
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                multiple
                class="visually-hidden"
                :disabled="isUploading"
                @change="handleFileChange"
              />
            </label>
            <p v-if="uploadError" class="error-text">{{ uploadError }}</p>
          </div>

          <div v-if="selectedAlbum.photos.length === 0" class="muted">
            Немає фото - додай перше вище
          </div>

          <ul v-else class="photo-grid">
            <li
              v-for="photo in selectedAlbum.photos"
              :key="photo.id"
              class="photo-card"
              :class="{ 'photo-card--cover': selectedAlbum.cover_photo?.id === photo.id }"
            >
              <img :src="photo.url" :alt="selectedAlbum.title" loading="lazy" />

              <div class="photo-card__actions">
                <button
                  class="photo-card__btn"
                  title="Пересунути раніше"
                  @click="movePhoto(photo, -1)"
                >
                  ‹
                </button>
                <button
                  class="photo-card__btn"
                  title="Зробити обкладинкою"
                  @click="handleSetCover(photo)"
                >
                  {{ selectedAlbum.cover_photo?.id === photo.id ? "★" : "☆" }}
                </button>
                <button
                  class="photo-card__btn"
                  title="Пересунути пізніше"
                  @click="movePhoto(photo, 1)"
                >
                  ›
                </button>
                <button
                  class="photo-card__btn photo-card__btn--danger"
                  title="Видалити фото"
                  @click="handleDeletePhoto(photo)"
                >
                  ×
                </button>
              </div>
            </li>
          </ul>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100dvh;
  background: var(--bg);
  color: var(--ink);
}

.dashboard__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--line);
}

.dashboard__title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  margin: 0;
}

.dashboard__body {
  display: grid;
  grid-template-columns: 20rem 1fr;
  min-height: calc(100dvh - 4rem);
}

.dashboard__sidebar {
  border-right: 1px solid var(--line);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  overflow-y: auto;
}

.dashboard__detail {
  padding: 1.5rem;
  overflow-y: auto;
}

.new-album,
.album-editor__meta {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.new-album input,
.new-album textarea,
.album-editor__meta input,
.album-editor__meta textarea {
  font-family: var(--font-body);
  font-size: 0.9rem;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--line);
  border-radius: 0.4rem;
  background: var(--surface);
  color: var(--ink);
  resize: vertical;
}

.album-editor__meta {
  max-width: 32rem;
  margin-bottom: 1.5rem;
}

.album-editor__upload {
  margin-bottom: 1.25rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.4rem;
  background: var(--accent);
  color: var(--accent-contrast);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}
.btn:hover:not(:disabled) {
  opacity: 0.9;
}
.btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.btn--ghost {
  background: transparent;
  border: 1px solid var(--line);
  color: var(--ink);
}

.muted {
  color: var(--ink-soft);
  font-size: 0.88rem;
}
.muted--center {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60vh;
}

.error-text {
  color: #b3453f;
  font-size: 0.82rem;
  margin: 0;
}

.album-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.album-list__item {
  display: flex;
  align-items: stretch;
  border-radius: 0.4rem;
  overflow: hidden;
  border: 1px solid transparent;
}

.album-list__item--active {
  border-color: var(--accent);
}

.album-list__select {
  all: unset;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.55rem 0.7rem;
  background: var(--surface);
  cursor: pointer;
}

.album-list__title {
  font-size: 0.9rem;
}

.album-list__meta {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--ink-soft);
}

.album-list__delete {
  all: unset;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.2rem;
  background: var(--surface);
  color: var(--ink-soft);
  cursor: pointer;
  font-size: 1.1rem;
}
.album-list__delete:hover {
  color: #b3453f;
}

.photo-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(11rem, 1fr));
  gap: 1rem;
}

.photo-card {
  position: relative;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 2px solid transparent;
  background: var(--surface);
}

.photo-card--cover {
  border-color: var(--accent);
}

.photo-card img {
  width: 100%;
  height: 8rem;
  object-fit: cover;
}

.photo-card__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.3rem 0.4rem;
  background: var(--surface);
  border-top: 1px solid var(--line);
}

.photo-card__btn {
  all: unset;
  cursor: pointer;
  padding: 0.15rem 0.4rem;
  font-size: 0.95rem;
  color: var(--ink);
}
.photo-card__btn--danger:hover {
  color: #b3453f;
}

@media (max-width: 800px) {
  .dashboard__body {
    grid-template-columns: 1fr;
  }
  .dashboard__sidebar {
    border-right: none;
    border-bottom: 1px solid var(--line);
  }
}
</style>