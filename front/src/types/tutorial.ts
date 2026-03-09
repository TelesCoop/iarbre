// Re-export driver.js types for convenience
export type { DriveStep, Driver, AllowedButtons } from "driver.js"

// Button constants to avoid hardcoding strings
export const DriverButton = {
  NEXT: "next",
  PREVIOUS: "previous",
  CLOSE: "close"
} as const

// Selectors for tutorial elements
export const TutorialSelector = {
  MAP_COMPONENT: '[data-cy="map-component"]',
  MAP_SIDE_PANEL: '[data-cy="map-side-panel"]',
  MOBILE_PANEL_HANDLE: '[data-cy="mobile-panel-handle"]',
  MOBILE_PANEL: '[data-cy="mobile-panel"]',
  LAYER_SWITCHER: '[data-cy="layer-switcher"]',
  MOBILE_LAYER_SWITCHER: '[data-cy="mobile-layer-switcher"]',
  MAP_BACKGROUND_SELECTOR: '[data-cy="bg-selector-toggle"]',
  PLANTABILITY_LEGEND: '[data-cy="plantability-legend"]',
  VULNERABILITY_LEGEND: '[data-cy="vulnerability-zones-legend"]',
  CLIMATE_ZONES_LEGEND: '[data-cy="climate-zones-legend"]',
  OPEN_FEEDBACK_BUTTON: '[data-cy="open-feedback-button"]',
  MOBILE_MENU_BUTTON: '[data-cy="mobile-menu-button"]',
  DASHBOARD_BUTTON: '[data-cy="dashboard-button"]',
  DASHBOARD_BUTTON_MOBILE: '[data-cy="dashboard-button-mobile"]',
  DRAWING_MODE_TOGGLE: '[data-cy="drawing-mode-toggle"]',
  BUTTON_3D: ".maplibregl-ctrl-3d-container",
  MAP_GEOCODER: '[data-cy="map-geocoder"]'
} as const
