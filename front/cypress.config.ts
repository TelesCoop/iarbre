import { defineConfig } from "cypress"
import codeCoverageTask from "@cypress/code-coverage/task"

export default defineConfig({
  e2e: {
    specPattern: "cypress/e2e/**/*.cy.ts",
    baseUrl: "http://localhost:4173",
    experimentalRunAllSpecs: true,
    viewportWidth: 1440,
    viewportHeight: 900,
    setupNodeEvents(on, config) {
      codeCoverageTask(on, config)
      on("before:browser:launch", (browser, launchOptions) => {
        if (browser.family === "chromium" && browser.name !== "electron") {
          launchOptions.args.push("--use-gl=swiftshader")
          launchOptions.args.push("--enable-webgl")
          launchOptions.args.push("--ignore-gpu-blocklist")
          launchOptions.args.push("--enable-unsafe-swiftshader")
        }
        return launchOptions
      })
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
