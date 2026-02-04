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
  MAP_CONFIG_DRAWER: '[data-cy="map-config-drawer"]',
  DRAWER_TOGGLE: '[data-cy="drawer-toggle"]',
  DRAWER_CLOSE_BUTTON: '[data-cy="drawer-close"]',
  MOBILE_PANEL_HANDLE: '[data-cy="mobile-panel-handle"]',
  LAYER_SWITCHER: '[data-cy="layer-switcher"]',
  MAP_LAYER_SWITCHER: '[data-cy="map-layer-switcher"]',
  MAP_BG_SWITCHER: '[data-cy="map-bg-switcher"]',
  MAP_BACKGROUND_SELECTOR: '[data-cy="bg-selector-toggle"]',
  PLANTABILITY_LEGEND: '[data-cy="plantability-legend"]',
  VULNERABILITY_LEGEND: '[data-cy="vulnerability-zones-legend"]',
  CLIMATE_ZONES_LEGEND: '[data-cy="climate-zones-legend"]',
  PLANT_VULNERABILITY_LEGEND: '[data-cy="plant-vulnerability-legend"]',
  OPEN_FEEDBACK_BUTTON: '[data-cy="open-feedback-button"]',
  MOBILE_MENU_BUTTON: '[data-cy="mobile-menu-button"]',
  MAP_FILTERS_STATUS: '[data-cy="map-filters-status"]'
} as const
