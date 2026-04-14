/**
 * Style constants for overlay map layers (QPV, communes boundaries, cadastre).
 * These constants centralise colors and widths so that visual changes
 * only need to be made in one place.
 */

// ---------------------------------------------------------------------------
// QPV (Quartiers Prioritaires de la Ville)
// ---------------------------------------------------------------------------

/** White halo drawn behind the QPV line so it stays legible on every basemap. */
export const QPV_CASING_COLOR = "#FFFFFF"
export const QPV_CASING_WIDTH = 3
export const QPV_CASING_OPACITY = 0.9

/** Main QPV border colour – vivid violet, visible on light, dark and satellite backgrounds. */
export const QPV_BORDER_COLOR = "#7C3AED"
export const QPV_BORDER_WIDTH = 1
export const QPV_BORDER_OPACITY = 1

// ---------------------------------------------------------------------------
// Communes (city boundaries)
// ---------------------------------------------------------------------------

export const BOUNDARY_BORDER_COLOR = "#426A45"
export const BOUNDARY_BORDER_WIDTH = 2.5
export const BOUNDARY_BORDER_OPACITY = 0.7

// ---------------------------------------------------------------------------
// Cadastre
// ---------------------------------------------------------------------------

export const CADASTRE_COLOR = "#8B6914"
export const CADASTRE_BORDER_WIDTH = 1
export const CADASTRE_BORDER_OPACITY = 0.5
export const CADASTRE_SELECTED_BORDER_WIDTH = 3
export const CADASTRE_SELECTED_BORDER_OPACITY = 1
export const CADASTRE_SELECTED_FILL_OPACITY = 0.3
export const CADASTRE_DEFAULT_FILL_OPACITY = 0.05
