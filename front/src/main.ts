import "./styles/main.css"
import PrimeVue from "primevue/config"
import Aura from "@primeuix/themes/aura"
import { definePreset } from "@primeuix/themes"
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
    preset: IArbrePreset
  }
})
app.use(ToastService)

app.mount("#app")
