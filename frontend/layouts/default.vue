<template>
  <v-app>
    <v-navigation-drawer absolute persistent permanent>
      <v-list
        class="overflow-scroll"
        height="85vh"
        v-model:selected="selectedSession"
        mandatory
      >
        <v-list-item v-if="sessions.length === 0" class="text-center mt-16">
          <span>
            <v-icon size="small">mdi-ghost-outline</v-icon>
            <v-icon size="large">mdi-ghost-outline</v-icon>
            <v-icon>mdi-ghost-outline</v-icon>
          </span>
          <h2 class="mt-4">You don't have any chats yet...</h2>
        </v-list-item>
        <v-list-item
          class="mx-2 my-2 py-2"
          v-else
          v-for="[index, session] in sessions.entries()"
          :key="index"
          :value="index"
          border
        >
          <template v-slot:append>
            <v-tooltip text="Copy chat URL" location="bottom">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon="mdi-content-copy"
                  variant="plain"
                ></v-btn>
              </template>
            </v-tooltip>
          </template>
          <v-list-item-title>
            {{ session.label }}
          </v-list-item-title>
        </v-list-item>
      </v-list>
      <v-list class="position-absolute bottom-0" width="100%">
        <v-list-item>
          <v-btn
            color="green"
            width="100%"
            prepend-icon="mdi-plus"
            variant="tonal"
            @click="dialog = true"
          >
            Create chat
          </v-btn>
        </v-list-item>
        <v-list-item>
          <v-btn
            color="red"
            width="100%"
            prepend-icon="mdi-logout"
            variant="tonal"
            @click="logout"
          >
            Logout
          </v-btn>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar :elevation="0" border class="px-4">
      <span>
        <strong v-if="authStore.selectedSession !== null">
          {{ authStore.sessions[authStore.selectedSession].label }} -
          <a
            :href="authStore.sessions[authStore.selectedSession].url"
            target="_blank"
            class="nolink"
            >{{ authStore.sessions[authStore.selectedSession].url }}</a
          >
        </strong>
        <strong v-else>TALK TO YOUR WEBSITE</strong>
      </span>
    </v-app-bar>

    <v-main>
      <slot v-if="!!selectedSession && selectedSession.length !== 0"></slot>
      <v-container v-else>
        <v-row class="mt-16">
          <v-col>
            <h1 class="text-center">
              Select an existing chat or create a new one
            </h1>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <v-footer app border absolute>
      <span>
        Logged in as <strong>{{ authStore.username }}</strong>
      </span>
      <v-spacer></v-spacer>
      <em>
        Pedro Boechat @ {{ new Date().getFullYear() }}. All rights reserved.
      </em>
    </v-footer>

    <v-dialog max-width="500" v-model="dialog">
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn
          v-bind="activatorProps"
          color="surface-variant"
          text="Open Dialog"
          variant="flat"
        ></v-btn>
      </template>

      <template v-slot:default>
        <v-form @submit.prevent="createChat" v-model="formValidation">
          <v-card title="Create new chat">
            <v-card-text>
              <v-row>
                <v-col>
                  <v-text-field
                    label="Chat name"
                    :rules="[(value) => !!value || 'Required field.']"
                    v-model="dialogLabel"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row>
                <v-col>
                  <v-text-field
                    label="Reference website"
                    :rules="[
                      (value) => {
                        if (
                          /\bhttps?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)\b/.test(
                            value,
                          )
                        ) {
                          return true;
                        }
                        return 'Invalid URL';
                      },
                      (value) => !!value || 'Required field.',
                    ]"
                    v-model="dialogWebsite"
                    @update:model-value="
                      if (dialogWebsite) {
                        dialogWebsite = dialogWebsite.trim();
                      }
                    "
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>

              <v-btn
                text="Cancel"
                color="red"
                variant="text"
                @click="resetCreate"
              ></v-btn>
              <v-btn
                text="Confirm"
                color="green"
                variant="text"
                type="submit"
                :disabled="!formValidation"
              ></v-btn>
            </v-card-actions>
          </v-card>
        </v-form>
      </template>
    </v-dialog>
  </v-app>
</template>

<script setup>
const config = useRuntimeConfig();
const authStore = useAuthStore();

const sessions = ref([]);
const selectedSession = ref();

const formValidation = ref(false);
const dialog = ref();
const dialogLabel = ref();
const dialogWebsite = ref();

function resetCreate() {
  dialog.value = false;
  formValidation.value = false;
  dialogLabel.value = null;
  dialogWebsite.value = null;
}

async function createChat() {
  await $fetch("/api/session", {
    baseURL: config.public.baseURL,
    body: {
      user_id: authStore.user_id,
      label: dialogLabel.value,
      url: dialogWebsite.value,
    },
    method: "POST",
  });
  resetCreate();
  await updateSessions();
}

async function updateSessions() {
  const sessionData = await $fetch("/api/session", {
    baseURL: config.public.baseURL,
    params: {
      user_id: authStore.user_id,
    },
    method: "GET",
  });
  sessions.value = sessionData.sessions;
}

function logout() {
  authStore.logout();
  return navigateTo({ path: "/login" });
}

watch(sessions, (value) => {
  authStore.setSessions(value);
});
watch(selectedSession, (value) => {
  if (sessions.length !== 0) {
    authStore.setSelectedSession(value[0]);
  }
});

onMounted(async () => {
  await updateSessions();
});
</script>

<style>
a.nolink {
  color: white;
  text-decoration: none;
  border-bottom: 1px dashed white;
  padding-bottom: 2px;
}
</style>
