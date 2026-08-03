<script setup>
import { ref, onMounted } from "vue";
import AlbumSection from "../components/AlbumSection.vue";
import Lightbox from "../components/Lightbox.vue";
import ThemeToggle from "../components/ThemeToggle.vue";
import { fetchAlbums, fetchAlbum } from "../api.js";

const albums = ref([]);
const isLoading = ref(true);
const error = ref(null);

const theme = ref(document.documentElement.getAttribute("data-theme") || "dark");

function toggleTheme() {
  theme.value = theme.value === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", theme.value);
  localStorage.setItem("theme", theme.value);
}

// --- лайтбокс (один на весь застосунок) ---
const lightbox = ref(null); // { album, index } | null

function openLightbox({ album, index }) {
  lightbox.value = { album, index };
}
function closeLightbox() {
  lightbox.value = null;
}
function updateLightboxIndex(index) {
  if (lightbox.value) lightbox.value = { ...lightbox.value, index };
}

async function loadAlbums() {
  isLoading.value = true;
  error.value = null;
  try {
    const list = await fetchAlbums(); // легкий список - лише порядок/назви/обкладинки
    // довантажуємо повну версію (з photos) для кожного, паралельно
    albums.value = await Promise.all(list.map((a) => fetchAlbum(a.slug)));
  } catch (e) {
    error.value = e.message || "Не вдалось завантажити альбоми";
  } finally {
    isLoading.value = false;
  }
}

onMounted(loadAlbums);
</script>

<template>
  <div class="page">
    <header class="page__header">
      <span class="page__logo">Фотоальбом</span>
      <ThemeToggle :theme="theme" @toggle="toggleTheme" />
    </header>

    <main class="page__main">
      <div v-if="isLoading" class="page__state">Завантаження...</div>

      <div v-else-if="error" class="page__state page__state--error">
        Не вдалося завантажити альбоми: {{ error }}
        <button class="page__retry" @click="loadAlbums">Спробувати ще раз</button>
      </div>

      <div v-else-if="albums.length === 0" class="page__state">
        Альбомів поки немає
      </div>

      <template v-else>
        <AlbumSection
          v-for="album in albums"
          :key="album.id"
          :album="album"
          @open-lightbox="openLightbox"
        />
      </template>
    </main>

    <Lightbox
      v-if="lightbox"
      :album="lightbox.album"
      :index="lightbox.index"
      @close="closeLightbox"
      @update:index="updateLightboxIndex"
    />
  </div>
</template>

<style scoped>
.page__header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.25rem;
  background: color-mix(in srgb, var(--bg) 82%, transparent);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--line);
}

.page__logo {
  font-family: var(--font-display);
  font-size: 1.05rem;
  letter-spacing: 0.01em;
}

.page__main {
  padding-top: 3.6rem; /* під висоту header */
  scroll-snap-type: y proximity;
}

.page__state {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: var(--ink-soft);
  font-size: 0.95rem;
  text-align: center;
  padding: 2rem;
}

.page__retry {
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--ink);
  padding: 0.5rem 1.1rem;
  border-radius: 999px;
  font-size: 0.85rem;
}
.page__retry:hover {
  border-color: var(--accent);
}
</style>
