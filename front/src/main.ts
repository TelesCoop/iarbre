import "./styles/main.css"
import { createApp } from "vue"
import { createPinia } from "pinia"
import { setWorkerUrl } from "maplibre-gl"
import maplibreWorkerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url"

import App from "./App.vue"
import router from "./router"
import { vTooltip } from "./directives/tooltip"
import { setupAnalytics } from "./analytics/matomo"

setWorkerUrl(maplibreWorkerUrl)

const app = createApp(App)
app.use(createPinia())
app.use(router)
setupAnalytics()

app.directive("tooltip", vTooltip)

app.mount("#app")
