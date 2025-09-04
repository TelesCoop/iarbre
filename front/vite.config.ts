import { fileURLToPath, URL } from "node:url"

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import tailwindcss from "@tailwindcss/vite"
import Components from "unplugin-vue-components/vite"
import { PrimeVueResolver } from "@primevue/auto-import-resolver"
import istanbul from "vite-plugin-istanbul"

export default defineConfig({
  plugins: [
    vue(),
    //@ts-ignore
    tailwindcss(),
    // in cas vue devtools is needed, also add
    // import vueDevTools from "vite-plugin-vue-devtools"
    // vueDevTools(),
    Components({
      resolvers: [PrimeVueResolver()]
    }),
    ...(process.env.CYPRESS_COVERAGE
      ? [
          istanbul({
            include: "src/**/*",
            exclude: ["node_modules", "tests/**/*", "cypress/**/*"],
            extension: [".ts", ".vue"],
            requireEnv: false
          })
        ]
      : [])
  ],
  server: {
    port: 3000,
    host: "0.0.0.0"
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url))
    }
  }
})
