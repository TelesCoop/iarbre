import { defineConfig } from "cypress"

export default defineConfig({
  e2e: {
    specPattern: "cypress/e2e/**/*.{cy,spec}.{js,jsx,ts,tsx}",
    baseUrl: "http://localhost:4173",
    experimentalRunAllSpecs: true,
    viewportWidth: 1440,
    viewportHeight: 900,
    setupNodeEvents(on, config) {
      require("@cypress/code-coverage/task")(on, config)
      return config
    }
  },

  component: {
    devServer: {
      framework: "vue",
      bundler: "vite"
    },
    viewportWidth: 1440,
    viewportHeight: 900
  }
})
