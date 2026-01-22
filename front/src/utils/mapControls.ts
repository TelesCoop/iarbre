import { Map } from "maplibre-gl"
import type { Ref } from "vue"

export const add3DControl = (use3D: Ref<boolean>, toggle3D: () => void) => {
  const button = document.createElement("button")
  button.className = "maplibregl-ctrl-3d"
  button.title = "Activer/désactiver la vue 3D"

  const iconColor = "#426A45"

  const updateButton = () => {
    button.innerHTML = use3D.value
      ? `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Top face -->
          <path d="M12 2L4 6.5L12 11L20 6.5L12 2Z" fill="${iconColor}" fill-opacity="0.5"/>
          <!-- Left face -->
          <path d="M4 6.5V15.5L12 20V11L4 6.5Z" fill="${iconColor}" fill-opacity="0.3"/>
          <!-- Right face -->
          <path d="M20 6.5V15.5L12 20V11L20 6.5Z" fill="${iconColor}" fill-opacity="0.15"/>
          <!-- Outline -->
          <path d="M12 2L4 6.5V15.5L12 20L20 15.5V6.5L12 2Z" stroke="${iconColor}" stroke-width="1.5" stroke-linejoin="round"/>
          <path d="M12 11L4 6.5M12 11L20 6.5M12 11V20" stroke="${iconColor}" stroke-width="1.5" stroke-linecap="round"/>
        </svg>`
      : `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L4 6.5V15.5L12 20L20 15.5V6.5L12 2Z" stroke="${iconColor}" stroke-width="1.5" stroke-linejoin="round"/>
          <path d="M12 11L4 6.5M12 11L20 6.5M12 11V20" stroke="${iconColor}" stroke-width="1.5" stroke-linecap="round"/>
        </svg>`
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
  button.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M11.51 7.77997C9.18004 7.77997 7.29004 9.66997 7.29004 12C7.29004 14.33 9.18004 16.22 11.51 16.22C13.84 16.22 15.73 14.33 15.73 12C15.73 9.66997 13.84 7.77997 11.51 7.77997ZM8.83004 11.99C8.83004 10.51 10.03 9.30997 11.51 9.30997C12.99 9.30997 14.19 10.51 14.19 11.99C14.19 13.47 12.99 14.67 11.51 14.67C10.03 14.67 8.83004 13.47 8.83004 11.99Z" fill="#426A45"/>
        <path fill-rule="evenodd" clip-rule="evenodd" d="M11.51 0.48999C11.93 0.48999 12.28 0.829989 12.28 1.25999V1.66999C17.39 2.03999 21.46 6.11999 21.84 11.23H22.25C22.67 11.23 23.02 11.57 23.02 12C23.02 12.43 22.68 12.77 22.25 12.77H21.84C21.47 17.88 17.39 21.95 12.28 22.33V22.74C12.28 23.16 11.94 23.51 11.51 23.51C11.08 23.51 10.74 23.17 10.74 22.74V22.33C5.63 21.96 1.56 17.88 1.18 12.77H0.77C0.35 12.77 0 12.43 0 12C0 11.57 0.34 11.23 0.77 11.23H1.18C1.55 6.11999 5.63 2.04999 10.74 1.66999V1.25999C10.74 0.839989 11.08 0.48999 11.51 0.48999ZM2.72 12.76H3.07C3.49 12.76 3.84 12.42 3.84 11.99C3.84 11.56 3.5 11.22 3.07 11.22H2.72C3.09 6.95999 6.48 3.56999 10.74 3.19999V3.54999C10.74 3.96999 11.08 4.31999 11.51 4.31999C11.94 4.31999 12.28 3.97999 12.28 3.54999V3.19999C16.54 3.56999 19.93 6.95999 20.3 11.22H19.95C19.53 11.22 19.18 11.56 19.18 11.99C19.18 12.42 19.52 12.76 19.95 12.76H20.3C19.93 17.02 16.54 20.41 12.28 20.78V20.43C12.28 20.01 11.94 19.66 11.51 19.66C11.08 19.66 10.74 20 10.74 20.43V20.78C6.48 20.41 3.09 17.02 2.72 12.76Z" fill="#426A45"/>
        </svg>
      `
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
