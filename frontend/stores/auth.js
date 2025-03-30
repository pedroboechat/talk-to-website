import { defineStore } from "pinia";
import { ref } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const config = useRuntimeConfig();

  const username = ref(null);
  const user_id = ref(null);
  const selectedSession = ref(null);
  const sessions = ref(null);

  const isAuthenticated = computed(() => !!username.value);

  async function setUser(data) {
    const userData = await $fetch("/api/login", {
      baseURL: config.public.baseURL,
      body: {
        username: data,
      },
      method: "POST",
    });

    username.value = data;
    user_id.value = userData.user_id;
  }

  async function setSessions(data) {
    sessions.value = data;
  }

  async function setSelectedSession(data) {
    selectedSession.value = data;
  }

  async function login(data) {
    await setUser(data);
  }

  function logout() {
    username.value = null;
    user_id.value = null;
    selectedSession.value = null;
    sessions.value = null;
  }

  return {
    username,
    user_id,
    sessions,
    selectedSession,
    setSessions,
    setSelectedSession,
    isAuthenticated,
    login,
    logout,
  };
});
