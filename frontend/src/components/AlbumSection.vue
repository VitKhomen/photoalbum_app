<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";

const props = defineProps({
  album: { type: Object, required: true },
  lightboxOpen: { type: Boolean, default: false },
  returnIndex: { type: Number, default: null },
});

const emit = defineEmits(["open-lightbox"]);

const photos = computed(() => props.album.photos || []);
const total = computed(() => photos.value.length);

const sectionEl = ref(null);
let observer = null;
let keydownActive = false;

function handleKeydown(e) {
  if (props.lightboxOpen) return;
  if (e.key === "ArrowRight") { e.preventDefault(); next(); }
  else if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
}

function activateKeydown() {
  if (!keydownActive) {
    window.addEventListener("keydown", handleKeydown);
    keydownActive = true;
  }
}
function deactivateKeydown() {
  if (keydownActive) {
    window.removeEventListener("keydown", handleKeydown);
    keydownActive = false;
  }
}

onMounted(() => {
  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting && entry.intersectionRatio >= 0.6) activateKeydown();
      else deactivateKeydown();
    },
    { threshold: [0, 0.6, 1] }
  );
  if (sectionEl.value) observer.observe(sectionEl.value);
});

onBeforeUnmount(() => {
  if (observer) observer.disconnect();
  deactivateKeydown();
});

function indexOfCover() {
  const coverId = props.album.cover_photo?.id ?? props.album.cover_photo_id;
  if (!coverId) return 0;
  const i = photos.value.findIndex((p) => p.id === coverId);
  return i >= 0 ? i : 0;
}

const currentIndex = ref(indexOfCover());
watch(
  () => props.returnIndex,
  (val) => {
    if (typeof val === "number" && val >= 0 && val < total.value) {
      currentIndex.value = val;
    }
  }
);

watch(
  () => [props.album.cover_photo?.id, props.album.cover_photo_id, photos.value.length],
  () => {
    currentIndex.value = indexOfCover();
  }
);

const currentPhoto = computed(() => photos.value[currentIndex.value]);

function pad(n) {
  return String(n).padStart(2, "0");
}

function next() {
  if (total.value === 0) return;
  currentIndex.value = (currentIndex.value + 1) % total.value;
}

function prev() {
  if (total.value === 0) return;
  currentIndex.value = (currentIndex.value - 1 + total.value) % total.value;
}
function goto(i) {
  currentIndex.value = i;
}

function openLightbox() {
  emit("open-lightbox", { album: props.album, index: currentIndex.value });
}

</script>

<template>
  <section class="album" ref="sectionEl" :aria-label="`Альбом: ${album.title}`">
    <div class="album__spine">
      <span class="album__spine-title">{{ album.title }}</span>
      <span class="album__spine-counter" v-if="total > 0">
        {{ pad(currentIndex + 1) }} / {{ pad(total) }}
      </span>
    </div>

    <div
      class="album__stage"
    >
      <button
        v-if="total > 1"
        class="album__nav album__nav--prev"
        @click="prev"
        aria-label="Попереднє фото"
      >
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
          <path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <button
        v-if="currentPhoto"
        class="album__photo-wrap"
        @click="openLightbox"
        :aria-label="`Відкрити на весь екран: ${album.title}, ${currentIndex + 1}`"
      >
        <video
          v-if="currentPhoto.media_type === 'video'"
          :src="currentPhoto.url"
          :style="currentPhoto.width && currentPhoto.height
            ? { aspectRatio: `${currentPhoto.width} / ${currentPhoto.height}` }
            : {}"
          autoplay
          muted
          loop
          playsinline
          preload="metadata"
        />
        <img
          v-else
          :src="currentPhoto.url"
          :alt="album.title"
          :style="currentPhoto.width && currentPhoto.height
            ? { aspectRatio: `${currentPhoto.width} / ${currentPhoto.height}` }
            : {}"
          loading="lazy"
        />
      </button>
      <div v-else class="album__empty">Немає фото в цьому альбомі</div>

      <button
        v-if="total > 1"
        class="album__nav album__nav--next"
        @click="next"
        aria-label="Наступне фото"
      >
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
          <path d="M9 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <div class="album__dots" v-if="total > 1">
      <button
        v-for="(p, i) in photos"
        :key="p.id"
        class="album__dot"
        :class="{ 'album__dot--active': i === currentIndex }"
        @click="goto(i)"
        :aria-label="`Перейти до фото ${i + 1}`"
      />
    </div>
  </section>
</template>

<style scoped>
.album {
  position: relative;
  display: flex;
  min-height: var(--section-desktop-h);
  border-bottom: 1px solid var(--line);
  scroll-snap-align: start;
  touch-action: pan-y;
  overflow-x: hidden;
  
}

.album__spine {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  width: 3.25rem;
  flex-shrink: 0;
  background: var(--accent);
  color: var(--accent-contrast);
  padding: 1.25rem 0;
  touch-action: pan-y;
}

.album__spine-title {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  white-space: nowrap;
}

.album__spine-counter {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  opacity: 0.75;
  letter-spacing: 0.04em;
}

.album__stage {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--surface);
  touch-action: pan-y;
  background: transparent;
}

.album__photo-wrap {
  all: unset;
  cursor: zoom-in;
  max-width: min(88%, 62rem);
  max-height: 92%;
  display: flex;
}

.album__photo-wrap img,
.album__photo-wrap video {
  max-width: 100%;
  max-height: calc(var(--section-desktop-h) - 4rem);
  width: auto;
  height: auto;
  object-fit: contain;
  box-shadow: var(--shadow);
}

.album__empty {
  color: var(--ink-soft);
  font-family: var(--font-body);
  font-size: 0.95rem;
}

.album__nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface) 80%, transparent);
  color: var(--ink);
  backdrop-filter: blur(6px);
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.album__nav:hover:not(:disabled) {
  transform: translateY(-50%) scale(1.05);
}

.album__nav:disabled {
  opacity: 0.25;
  cursor: default;
}

.album__nav--prev {
  left: 1.25rem;
}
.album__nav--next {
  right: 1.25rem;
}


.album__dots {
  position: absolute;
  bottom: 0.9rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 0.4rem;
  z-index: 2;
}

.album__dot {
  all: unset;
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 999px;
  background: var(--ink-soft);
  opacity: 0.4;
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.album__dot--active {
  opacity: 1;
  background: var(--accent);
  transform: scale(1.3);
}

/* --- Мобільна версія: альбом на весь екран, "корінець" - знизу --- */
@media (max-width: 720px) {
  .album {
    flex-direction: column;
    min-height: auto;
    height: auto;
    padding-bottom: 2.8rem;
    padding-top: 0.70rem;
    touch-action: pan-y;
    overflow-x: hidden;
  }

  .album__spine {
    writing-mode: horizontal-tb;
    transform: none;
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 0.85rem 1.1rem;
    gap: 0.5rem;
    touch-action: pan-y;
  }

  .album__spine-title {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .album__photo-wrap img,
  .album__photo-wrap video {
    max-height: 58dvh;
  }

  .album__stage {
    flex: none;           
    padding: 0.75rem 0 1rem;
  }

  .album__nav {
    display: flex;
    width: 2.25rem;
    height: 2.25rem;
    top: auto;
    bottom: 3.2rem; /* трохи вище крапок-індикаторів */
    transform: none;
  }
  .album__nav--prev { left: 0.75rem; }
  .album__nav--next { right: 0.75rem; }

  .album__nav:hover:not(:disabled),
  .album__nav:active:not(:disabled) {
    transform: scale(1.05);
  }
}
</style>
