import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";
import { createVuetify, type ThemeDefinition } from "vuetify";

const customTheme: ThemeDefinition = {
  dark: true,
  colors: {
    background: "#202020",
    surface: "#111",
  },
};

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({
    theme: { defaultTheme: "customTheme", themes: { customTheme } },
  });
  app.vueApp.use(vuetify);
});
