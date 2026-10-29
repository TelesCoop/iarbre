import { defineConfig } from "cypress"

export default defineConfig({
  e2e: {
    specPattern: "cypress/prod/**/*.cy.ts",
    supportFile: "cypress/support/e2e-prod.ts",
    baseUrl: "https://carte.iarbre.fr",
    viewportWidth: 1440,
    viewportHeight: 900,
    defaultCommandTimeout: 15000,
    retries: { runMode: 2, openMode: 0 },
    video: false,
    setupNodeEvents(on) {
      on("before:browser:launch", (browser, launchOptions) => {
        if (browser.family === "chromium" && browser.name !== "electron") {
          launchOptions.args.push("--use-gl=swiftshader")
          launchOptions.args.push("--enable-webgl")
          launchOptions.args.push("--ignore-gpu-blocklist")
          launchOptions.args.push("--enable-unsafe-swiftshader")
        }
        return launchOptions
      })
    }
  }
})
