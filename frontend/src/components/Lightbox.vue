<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";

const props = defineProps({
  album: { type: Object, required: true },
  index: { type: Number, required: true },
});

const emit = defineEmits(["close", "update:index"]);

const photos = computed(() => props.album.photos || []);
const total = computed(() => photos.value.length);
const current = computed(() => photos.value[props.index]);

function pad(n) {
  return String(n).padStart(2, "0");
}

function next() {
  if (total.value === 0) return;
  emit("update:index", (props.index + 1) % total.value);
}

function prev() {
  if (total.value === 0) return;
  emit("update:index", (props.index - 1 + total.value) % total.value);
}

// --- слайдшоу ---
const isPlaying = ref(false);
let slideshowTimer = null;
const SLIDESHOW_DELAY = 3500;

function slideshowAdvance() {
  // на відміну від ручного next() - тут по колу, не зупиняється на останньому фото
  const nextIndex = (props.index + 1) % total.value;
  emit("update:index", nextIndex);
  scheduleSlideshow();
}

function scheduleSlideshow() {
  clearTimeout(slideshowTimer);
  slideshowTimer = setTimeout(slideshowAdvance, SLIDESHOW_DELAY);
}

function stopSlideshow() {
  isPlaying.value = false;
  clearTimeout(slideshowTimer);
}

function toggleSlideshow() {
  if (isPlaying.value) {
    stopSlideshow();
  } else {
    isPlaying.value = true;
    scheduleSlideshow();
  }
}

// ручна навігація під час слайдшоу - перезапускаємо таймер, а не зупиняємо
function nextWithReset() {
  next();
  if (isPlaying.value) scheduleSlideshow();
}
function prevWithReset() {
  prev();
  if (isPlaying.value) scheduleSlideshow();
}

function close() {
  stopSlideshow();
  emit("close");
}

function requestFullscreenSafe() {
  const el = document.documentElement;
  const request =
    el.requestFullscreen ||
    el.webkitRequestFullscreen || // Safari
    el.mozRequestFullScreen ||    // старий Firefox
    el.msRequestFullscreen;       // старий Edge/IE

  if (request) {
    request.call(el).catch(() => {
      // браузер відмовив (наприклад, немає user-gesture чи не підтримується
      // на цьому пристрої) - просто лишаємось у звичайному режимі, без помилки
    });
  }
}

function exitFullscreenSafe() {
  const exit =
    document.exitFullscreen ||
    document.webkitExitFullscreen ||
    document.mozCancelFullScreen ||
    document.msExitFullscreen;

  const isFullscreen =
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement;

  if (exit && isFullscreen) {
    exit.call(document).catch(() => {});
  }
}

function onKeydown(e) {
  if (e.key === "Escape") close();
  if (e.key === "ArrowRight") nextWithReset();
  if (e.key === "ArrowLeft") prevWithReset();
}

let touchStartX = 0;
function onTouchStart(e) {
  touchStartX = e.touches[0].clientX;
}
function onTouchEnd(e) {
  const dx = e.changedTouches[0].clientX - touchStartX;
  const threshold = 45;
  if (dx <= -threshold) nextWithReset();
  else if (dx >= threshold) prevWithReset();
}

let savedScrollY = 0;

onMounted(() => {
  window.addEventListener("keydown", onKeydown);

  savedScrollY = window.scrollY;
  document.body.style.position = "fixed";
  document.body.style.top = `-${savedScrollY}px`;
  document.body.style.left = "0";
  document.body.style.right = "0";
  document.body.style.overflow = "hidden";

  requestFullscreenSafe();
});
onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKeydown);
  clearTimeout(slideshowTimer);

  document.body.style.position = "";
  document.body.style.top = "";
  document.body.style.left = "";
  document.body.style.right = "";
  document.body.style.overflow = "";
  window.scrollTo(0, savedScrollY); // повертаємось точно туди, звідки відкрили

  exitFullscreenSafe();
});
</script>

<template>
  <div
    class="lightbox"
    role="dialog"
    aria-modal="true"
    :aria-label="`Перегляд фото: ${album.title}`"
    @click.self="close"
    @touchstart="onTouchStart"
    @touchend="onTouchEnd"
  >

    <figure class="lightbox__figure" v-if="current">
      <video
        v-if="current.media_type === 'video'"
        :key="current.id"
        :src="current.url"
        controls
        autoplay
        playsinline
        preload="metadata"
      />
      <img
        v-else
        :src="current.url"
        :alt="album.title"
      />

      <figcaption class="lightbox__caption">
        <span class="lightbox__title">{{ album.title }}</span>
        <span class="lightbox__counter">{{ pad(index + 1) }} / {{ pad(total) }}</span>
      </figcaption>

      <!-- Кнопки внизу: prev | play + close | next -->
      <div class="lightbox__controls">
        <button
          v-if="total > 1"
          class="lightbox__nav lightbox__nav--prev"
          @click="prevWithReset"
          aria-label="Попереднє фото"
        >
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
            <path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div v-else class="lightbox__nav-spacer"></div>

        <button
          class="lightbox__play"
          @click="toggleSlideshow"
          :aria-label="isPlaying ? 'Зупинити слайдшоу' : 'Запустити слайдшоу'"
        >
          <svg v-if="!isPlaying" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M6 5h4v14H6zM14 5h4v14h-4z"/>
          </svg>
        </button>

        <button class="lightbox__close" @click="close" aria-label="Закрити">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
            <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>

        <button
          v-if="total > 1"
          class="lightbox__nav lightbox__nav--next"
          @click="nextWithReset"
          aria-label="Наступне фото"
        >
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
            <path d="M9 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div v-else class="lightbox__nav-spacer"></div>
      </div>
    </figure>

  </div>
</template>

<style scoped>
.lightbox {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: var(--scrim);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: lightbox-in var(--transition-slide);
}

@keyframes lightbox-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.lightbox__figure {
  margin: 0;
  max-width: min(92vw, 78rem);
  max-height: 88dvh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.9rem;
}
.lightbox__controls {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.25rem;
}

.lightbox__figure img,
.lightbox__figure video {
  max-width: 100%;
  max-height: 78dvh;
  object-fit: contain;
}

.lightbox__caption {
  display: flex;
  align-items: baseline;
  gap: 0.9rem;
  color: #f2f0ea;
}

.lightbox__title {
  font-family: var(--font-display);
  font-size: 1rem;
}

.lightbox__counter {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  opacity: 0.65;
  letter-spacing: 0.04em;
}

/* === Кнопки Close і Play — тепер внизу === */
.lightbox__close,
.lightbox__play {
  all: unset;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  color: #f2f0ea;
  cursor: pointer;
  background: rgba(0, 0, 0, 0.35); /* щоб було видно на світлих фото */
}

.lightbox__close:hover,
.lightbox__play:hover {
  background: rgba(255, 255, 255, 0.15);
}

.lightbox__nav {
  all: unset;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: 999px;
  color: #f2f0ea;
  cursor: pointer;
}
.lightbox__nav:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.lightbox__nav--prev { left: 1rem; }
.lightbox__nav--next { right: 1rem; }

@media (max-width: 720px) {
  .lightbox__play {
    bottom: max(1rem, env(safe-area-inset-bottom));
    right: 3.75rem;
    top: auto;
  }
  .lightbox__close {
    bottom: max(1rem, env(safe-area-inset-bottom));
    top: auto;
  }

  .lightbox__nav {
    width: 2.5rem;
    height: 2.5rem;
    background: rgba(0, 0, 0, 0.35);
  }
}
</style>
