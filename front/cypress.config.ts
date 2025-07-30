import { defineConfig } from "cypress"

export default defineConfig({
  e2e: {
    specPattern: "cypress/e2e/**/*.{cy,spec}.{js,jsx,ts,tsx}",
    baseUrl: "http://localhost:4173",
    experimentalRunAllSpecs: true,
    viewportWidth: 1440,
    viewportHeight: 900
  }
})
