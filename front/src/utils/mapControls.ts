import { Map } from "maplibre-gl"
import type { Ref } from "vue"

const SVG_OPEN =
  '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#426A45" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'

// Isometric box — reads as the 3D toggle; the active state is shown by the button.
const CUBE_ICON = `${SVG_OPEN}
  <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
  <path d="m3.3 7 8.7 5 8.7-5" />
  <path d="M12 22V12" />
</svg>`

// Crosshair — "recenter the map" affordance.
const CROSSHAIR_ICON = `${SVG_OPEN}
  <circle cx="12" cy="12" r="6" />
  <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
  <circle cx="12" cy="12" r="1.6" fill="#426A45" stroke="none" />
</svg>`

export const add3DControl = (use3D: Ref<boolean>, toggle3D: () => void) => {
  const button = document.createElement("button")
  button.className = "maplibregl-ctrl-3d"
  button.title = "Activer/désactiver la vue 3D"
  button.innerHTML = CUBE_ICON
  button.classList.toggle("is-active", use3D.value)

  button.addEventListener("click", () => {
    toggle3D()
    button.classList.toggle("is-active", use3D.value)
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
