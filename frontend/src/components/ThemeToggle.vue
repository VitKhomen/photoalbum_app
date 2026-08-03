<script setup>
defineProps({
  theme: { type: String, required: true }, // 'light' | 'dark'
});
defineEmits(["toggle"]);
</script>

<template>
  <button
    class="theme-toggle"
    @click="$emit('toggle')"
    :aria-label="theme === 'dark' ? 'Увімкнути світлу тему' : 'Увімкнути темну тему'"
  >
    <svg v-if="theme === 'dark'" viewBox="0 0 24 24" width="19" height="19" fill="none">
      <circle cx="12" cy="12" r="4.2" stroke="currentColor" stroke-width="1.6"/>
      <path stroke="currentColor" stroke-width="1.6" stroke-linecap="round"
        d="M12 2.5v2M12 19.5v2M21.5 12h-2M4.5 12h-2M18.4 5.6l-1.4 1.4M7 17l-1.4 1.4M18.4 18.4l-1.4-1.4M7 7L5.6 5.6"/>
    </svg>
    <svg v-else viewBox="0 0 24 24" width="19" height="19" fill="none">
      <path stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"
        d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z"/>
    </svg>
  </button>
</template>

<style scoped>
.theme-toggle {
  all: unset;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  border: 1px solid var(--line);
  color: var(--ink);
  background: var(--surface);
  transition: transform var(--transition-fast), border-color var(--transition-fast);
}
.theme-toggle:hover {
  border-color: var(--accent);
  transform: rotate(12deg);
}
</style>
