import js from "@eslint/js"
import globals from "globals"
import pluginVue from "eslint-plugin-vue"
import pluginCypress from "eslint-plugin-cypress"
import skipFormatting from "@vue/eslint-config-prettier/skip-formatting"
import { defineConfigWithVueTs, vueTsConfigs } from "@vue/eslint-config-typescript"

export default defineConfigWithVueTs(
  {
    ignores: [
      "dist/**",
      "coverage/**",
      ".nyc_output/**",
      "components.d.ts",
      "public/tarteaucitron/**"
    ]
  },
  js.configs.recommended,
  pluginVue.configs["flat/recommended"],
  vueTsConfigs.base,
  vueTsConfigs.eslintRecommended,
  {
    files: ["cypress/e2e/**/*.{cy,spec}.{js,ts,jsx,tsx}", "cypress/support/**/*.{js,ts,jsx,tsx}"],
    ...pluginCypress.configs.recommended
  },
  {
    files: ["**/*.{ts,tsx,vue}"],
    rules: {
      "no-unused-vars": "off",
      "@typescript-eslint/no-unused-vars": "error"
    }
  },
  {
    files: ["scripts/**/*.mjs", "*.config.{js,cjs,mjs,ts}"],
    languageOptions: { globals: globals.node }
  },
  skipFormatting
)
