import { useAuthStore } from "~/stores/auth";

export default defineNuxtRouteMiddleware((to, _from) => {
  const authStore = useAuthStore();

  if (!authStore.isAuthenticated && to.path !== "/login") {
    return navigateTo({ path: "/login" });
  }
});
