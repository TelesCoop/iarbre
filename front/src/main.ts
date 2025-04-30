import "./styles/main.css"
import PrimeVue from "primevue/config"
import { createApp } from "vue"
import { createPinia } from "pinia"
import ToastService from "primevue/toastservice"

import App from "./App.vue"
import router from "./router"
import { IArbrePreset } from "./theme/iArbre"

const app = createApp(App)
app.use(createPinia())
app.use(router)

app.use(PrimeVue, {
  theme: {
    preset: IArbrePreset,
    options: {
      darkModeSelector: false
    }
  }
})
app.use(ToastService)

app.mount("#app")
