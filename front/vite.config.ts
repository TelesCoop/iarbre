import { fileURLToPath, URL } from "node:url"

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import tailwindcss from "@tailwindcss/vite"
import Components from "unplugin-vue-components/vite"
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
      dirs: ["src/components"],
      dts: true
    }),
    istanbul({
      include: "src/**/*.{ts,vue}",
      exclude: [
        "node_modules",
        "tests/**/*",
        "cypress/**/*",
        "**/*.d.ts",
        "**/*.spec.ts",
        "**/__tests__/**",
        "src/utils/**",
        "src/composables/**",
        "src/services/**"
      ],
      extension: [".ts", ".vue"],
      requireEnv: false,
      cypress: true,
      forceBuildInstrument: process.env.CYPRESS_COVERAGE === "true"
    })
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
