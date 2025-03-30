<template>
  <v-container>
    <v-virtual-scroll
      v-if="messages !== null"
      ref="virtualScroll"
      :items="messages"
      max-height="60vh"
      class="px-2 virtual-scroll"
    >
      <template v-slot:default="{ item, index }">
        <v-row
          no-gutters
          :justify="chatLayout[item.kind].justify"
          :id="`chat-message-${index}`"
        >
          <v-col cols="5">
            <v-card elevation="16" :color="chatLayout[item.kind].color">
              <v-card-title
                :class="`text-${chatLayout[item.kind].justify} text-white`"
              >
                <v-icon>{{ chatLayout[item.kind].symbol }}</v-icon>
              </v-card-title>
              <v-card-item>
                <v-card-text class="text-white pa-0">
                  <h4>{{ item.message }}</h4>
                </v-card-text>
              </v-card-item>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </v-virtual-scroll>
    <v-row class="chat-input">
      <v-col>
        <v-textarea
          no-resize
          rows="3"
          label="Your message"
          variant="outlined"
          v-model="chatInput"
          :loading="chatDisabled"
          :disabled="chatDisabled"
          @keydown.ctrl.enter="sendMessage"
        >
          <template v-slot:append>
            <v-btn
              height="100%"
              variant="tonal"
              @click="sendMessage"
              stacked
              prepend-icon="mdi-send"
            >
              <p style="font-size: 10px">CTRL+ENTER</p>
            </v-btn>
          </template>
        </v-textarea>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
const config = useRuntimeConfig();
const authStore = useAuthStore();

const chatLayout = {
  ai: {
    justify: "start",
    color: "green",
    symbol: "mdi-robot-happy",
  },
  human: {
    justify: "end",
    color: "cyan",
    symbol: "mdi-emoticon-happy",
  },
};

const chatInput = ref();
const chatDisabled = ref(false);
const virtualScroll = ref();
const messages = ref([]);

function waitForElm(selector) {
  return new Promise((resolve) => {
    if (document.querySelector(selector)) {
      return resolve(document.querySelector(selector));
    }

    const observer = new MutationObserver((mutations) => {
      if (document.querySelector(selector)) {
        observer.disconnect();
        resolve(document.querySelector(selector));
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  });
}

async function scrollToLast(index) {
  await waitForElm(".virtual-scroll");
  virtualScroll.value.scrollToIndex(Math.max(index, 0));
}

async function updateMessages() {
  const messageData = await $fetch("/api/messages", {
    baseURL: config.public.baseURL,
    params: {
      session_id: authStore.sessions[authStore.selectedSession].session_id,
    },
    method: "GET",
  });

  chatInput.value = null;
  messages.value = null;
  messages.value = await messageData.messages;

  await scrollToLast(messageData.messages.length - 1);
}

async function sendMessage() {
  chatDisabled.value = true;

  try {
    await $fetch("/api/ask", {
      baseURL: config.public.baseURL,
      body: {
        url: authStore.sessions[authStore.selectedSession].url,
        session_id: authStore.sessions[authStore.selectedSession].session_id,
        message: chatInput.value,
      },
      method: "POST",
    });

    await updateMessages();
  } catch (error) {
    console.error(error);
  }

  chatDisabled.value = false;
}

watch(
  () => authStore.selectedSession,
  async () => {
    if (authStore.selectedSession !== null) {
      await updateMessages();
    }
  },
);

onUpdated(async () => {
  await updateMessages();
});
</script>

<style>
.chat-input .v-input__append {
  padding-top: 0 !important;
}

.chat-input {
  position: absolute;
  bottom: 5vh;
  left: 21vw;
  right: 1vw;
}
</style>
