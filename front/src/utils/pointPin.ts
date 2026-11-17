import { Marker } from "maplibre-gl"

const PIN_SVG = `<svg width="28" height="38" viewBox="0 0 28 38" aria-hidden="true">
  <path d="M14 37C14 37 26 22.5 26 14A12 12 0 0 0 2 14C2 22.5 14 37 14 37Z"
    fill="var(--color-primary-900)" stroke="#FFFFFF" stroke-width="2" />
  <circle cx="14" cy="14" r="4.5" fill="#FFFFFF" />
</svg>`

export const createPointPin = (): Marker => {
  const element = document.createElement("div")
  element.innerHTML = PIN_SVG
  element.dataset.cy = "point-pin"
  element.style.pointerEvents = "none"
  element.style.filter = "drop-shadow(0 2px 3px rgba(0, 0, 0, 0.35))"
  return new Marker({ element, anchor: "bottom" })
}
