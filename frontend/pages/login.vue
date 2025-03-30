<template>
  <v-container>
    <v-form @submit.prevent="doLogin" v-model="formValidation">
      <v-row no-gutters class="mt-16">
        <v-col cols="12">
          <v-row justify="center">
            <v-col cols="auto">
              <h1>TALK TO YOUR WEBSITE</h1>
            </v-col>
          </v-row>
          <v-row justify="center" class="mt-16">
            <v-col cols="12" md="4">
              <v-text-field
                prepend-inner-icon="mdi-account-outline"
                label="Username"
                variant="outlined"
                v-model="username"
                @update:model-value="
                  (value) =>
                    (username = value.toLowerCase().replace(/\s|\W/g, ''))
                "
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="12" md="4">
              <v-btn
                variant="outlined"
                width="100%"
                type="submit"
                :disabled="!username || username.length === 0"
              >
                Login
              </v-btn>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-form>
  </v-container>
</template>

<script setup>
definePageMeta({
  layout: false,
});

const authStore = useAuthStore();

const username = ref();
const formValidation = ref(false);

async function doLogin() {
  if (username.value) {
    await authStore.login(username.value.toLowerCase());
    navigateTo({ path: "/" });
  }
}
</script>
