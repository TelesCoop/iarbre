import { defineConfig } from "cypress"

export default defineConfig({
  e2e: {
    specPattern: "cypress/e2e/**/*.{cy,spec}.{js,jsx,ts,tsx}",
    baseUrl: "http://localhost:4173",
    experimentalRunAllSpecs: true,
    viewportWidth: 1440,
    viewportHeight: 900,

    // Register code coverage task in e2e mode
    async setupNodeEvents(on, config) {
      const codeCoverage = await import("@cypress/code-coverage/task")
      codeCoverage.default(on, config)
      return config
    }
  },

  component: {
    devServer: {
      framework: "vue",
      bundler: "vite"
    },
    viewportWidth: 1440,
    viewportHeight: 900,

    // Register code coverage task in component mode
    async setupNodeEvents(on, config) {
      const codeCoverage = await import("@cypress/code-coverage/task")
      codeCoverage.default(on, config)
      return config
    }
  }
})
