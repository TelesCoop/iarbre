import { fileURLToPath, URL } from "node:url"

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    //@ts-ignore
    tailwindcss()
    // in cas vue devtools is needed, also add
    // import vueDevTools from "vite-plugin-vue-devtools"
    // vueDevTools(),
  ],
  server: {
    port: 3000
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url))
    }
  }
})
