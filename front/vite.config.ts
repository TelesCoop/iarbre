import { fileURLToPath, URL } from "node:url"

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import vueDevTools from "vite-plugin-vue-devtools"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  server: {
    port: 3000
  },
  css: {
    postcss: "./postcss.config.mjs"
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url))
    }
  }
})
