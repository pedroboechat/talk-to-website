// https://nuxt.com/docs/api/configuration/nuxt-config
import vuetify, { transformAssetUrls } from "vite-plugin-vuetify";

export default defineNuxtConfig({
  app: {
    head: {
      title: "TALK TO YOUR WEBSITE",
    },
  },
  build: {
    transpile: ["vuetify"],
  },
  compatibilityDate: "2024-08-12",
  modules: [
    (_options, nuxt) => {
      nuxt.hooks.hook("vite:extendConfig", (config) => {
        // @ts-expect-error
        config.plugins.push(vuetify({ autoImport: true }));
      });
    },
    "@pinia/nuxt",
  ],
  runtimeConfig: {
    public: {
      baseURL: process.env.NUXT_PUBLIC_BASE_URL,
    },
  },
  ssr: false,
  vite: {
    vue: {
      template: {
        transformAssetUrls,
      },
    },
  },
});
