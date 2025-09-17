const plugins: any[] = []
if (process.env.NODE_ENV === "test" || process.env.CYPRESS_COVERAGE) {
  plugins.push([
    "babel-plugin-istanbul",
    {
      // specify some options for NYC instrumentation here
      // like tell it to instrument both TypeScript and Vue files
      extension: [".ts", ".vue"]
    }
  ])
}

export default {
  presets: ["@vue/app"],
  plugins
}
