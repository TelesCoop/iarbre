import "./styles/main.css"
import { createApp } from "vue"
import { createPinia } from "pinia"

import App from "./App.vue"
import router from "./router"
import { vTooltip } from "./directives/tooltip"

const app = createApp(App)
app.use(createPinia())
app.use(router)

app.directive("tooltip", vTooltip)

app.mount("#app")
