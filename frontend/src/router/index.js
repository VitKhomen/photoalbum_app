import { createRouter, createWebHistory } from "vue-router";
import PublicPage from "../views/PublicPage.vue";
import { useAuth } from "../stores/auth.js";

const routes = [
  { path: "/", name: "home", component: PublicPage },
  {
    path: "/admin/login",
    name: "admin-login",
    component: () => import("../views/AdminLogin.vue"),
  },
  {
    path: "/admin",
    name: "admin-dashboard",
    component: () => import("../views/AdminDashboard.vue"),
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const { isAuthenticated } = useAuth();
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return { name: "admin-login" };
  }
});

export default router;