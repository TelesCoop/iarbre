import { defineConfig } from "cypress"
import codeCoverageTask from "@cypress/code-coverage/task.js"

export default defineConfig({
  e2e: {
    specPattern: "cypress/e2e/**/*.cy.ts",
    baseUrl: "http://localhost:4173",
    experimentalRunAllSpecs: true,
    viewportWidth: 1440,
    viewportHeight: 900,
    setupNodeEvents(on, config) {
      codeCoverageTask(on, config)
      return config
    }
  },

  component: {
    specPattern: "cypress/components/**/*.cy.ts",
    devServer: {
      framework: "vue",
      bundler: "vite"
    },
    viewportWidth: 1440,
    viewportHeight: 900,
    setupNodeEvents(on, config) {
      codeCoverageTask(on, config)
      return config
    }
  }
})
