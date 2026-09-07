import "./styles/main.css"
import { createApp } from "vue"
import { createPinia } from "pinia"

import App from "./App.vue"
import router from "./router"
import { vTooltip } from "./directives/tooltip"
import { setupAnalytics } from "./analytics/matomo"

const app = createApp(App)
app.use(createPinia())
app.use(router)
setupAnalytics()

app.directive("tooltip", vTooltip)

app.mount("#app")
