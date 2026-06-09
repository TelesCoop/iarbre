import { Map } from "maplibre-gl"
import type { Ref } from "vue"

const CROSSHAIR_ICON = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#426A45" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="6" />
  <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
  <circle cx="12" cy="12" r="1.6" fill="#426A45" stroke="none" />
</svg>`

export const add3DControl = (use3D: Ref<boolean>, toggle3D: () => void) => {
  const button = document.createElement("button")
  button.className = "maplibregl-ctrl-3d"
  button.title = "Activer/désactiver la vue 3D"

  // Text label rather than an icon: feedback was that an icon didn't read as a 3D switch.
  const updateButton = () => {
    button.innerHTML = use3D.value ? "2D" : "3D"
    button.classList.toggle("is-active", use3D.value)
  }
  updateButton()

  button.addEventListener("click", () => {
    toggle3D()
    updateButton()
  })

  const container = document.createElement("div")
  container.className = "maplibregl-ctrl maplibregl-ctrl-group maplibregl-ctrl-3d-container"
  container.appendChild(button)
  return container
}

export const addCenterControl = (map: Map) => {
  const button = document.createElement("button")
  button.className = "maplibregl-ctrl-center"
  button.title = "Centrer la carte sur Lyon Part-Dieu"
  button.innerHTML = CROSSHAIR_ICON
  button.addEventListener("click", () => {
    map.flyTo({
      center: [4.8611, 45.760547],
      zoom: 14,
      duration: 1000
    })
  })

  const container = document.createElement("div")
  container.className = "maplibregl-ctrl maplibregl-ctrl-group maplibregl-ctrl-center-container"
  container.appendChild(button)
  return container
}
