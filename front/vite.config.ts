import { fileURLToPath, URL } from "node:url"

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue()
    // in cas vue devtools is needed, also add
    // import vueDevTools from "vite-plugin-vue-devtools"
    // vueDevTools(),
  ],
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
