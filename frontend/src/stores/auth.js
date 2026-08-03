import { ref, computed } from "vue";
import { loginRequest } from "../api.js";

const TOKEN_KEY = "admin_token";

// один спільний реактивний стан на весь застосунок (простий singleton-стор,
// без Pinia - для такого розміру проєкту цього достатньо)
const token = ref(localStorage.getItem(TOKEN_KEY) || null);

const isAuthenticated = computed(() => !!token.value);

async function login(username, password) {
  const data = await loginRequest(username, password);
  token.value = data.access_token;
  localStorage.setItem(TOKEN_KEY, token.value);
}

function logout() {
  token.value = null;
  localStorage.removeItem(TOKEN_KEY);
}

export function useAuth() {
  return { token, isAuthenticated, login, logout };
}