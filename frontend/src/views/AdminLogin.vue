<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "../stores/auth.js";

const router = useRouter();
const { login } = useAuth();

const username = ref("");
const password = ref("");
const error = ref(null);
const isSubmitting = ref(false);

async function onSubmit() {
  error.value = null;
  isSubmitting.value = true;
  try {
    await login(username.value, password.value);
    router.push("/admin");
  } catch (e) {
    error.value = e.message || "Не вдалося увійти";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="login-page">
    <form class="login-card" @submit.prevent="onSubmit">
      <h1 class="login-card__title">Вхід в адмінку</h1>

      <label class="login-field">
        <span class="login-field__label">Логін</span>
        <input
          v-model="username"
          type="text"
          autocomplete="username"
          required
        />
      </label>

      <label class="login-field">
        <span class="login-field__label">Пароль</span>
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
        />
      </label>

      <p v-if="error" class="login-card__error">{{ error }}</p>

      <button class="login-card__submit" type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? "Входимо..." : "Увійти" }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  padding: 1.5rem;
}

.login-card {
  width: 100%;
  max-width: 22rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 0.75rem;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
  box-shadow: var(--shadow);
}

.login-card__title {
  font-family: var(--font-display);
  font-size: 1.4rem;
  margin: 0 0 0.4rem;
  color: var(--ink);
}

.login-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.login-field__label {
  font-size: 0.82rem;
  color: var(--ink-soft);
}

.login-field input {
  font-family: var(--font-body);
  font-size: 0.95rem;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--line);
  border-radius: 0.4rem;
  background: var(--bg);
  color: var(--ink);
}

.login-field input:focus-visible {
  border-color: var(--accent);
}

.login-card__error {
  margin: 0;
  font-size: 0.85rem;
  color: #b3453f;
}

.login-card__submit {
  margin-top: 0.4rem;
  padding: 0.65rem;
  border: none;
  border-radius: 0.4rem;
  background: var(--accent);
  color: var(--accent-contrast);
  font-size: 0.95rem;
  font-weight: 500;
  transition: opacity var(--transition-fast);
}

.login-card__submit:hover:not(:disabled) {
  opacity: 0.9;
}

.login-card__submit:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>