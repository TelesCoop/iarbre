/**
 * Calculates the relative luminance of a color
 * @param r Red component (0-255)
 * @param g Green component (0-255)
 * @param b Blue component (0-255)
 * @returns Relative luminance value (0-1)
 */
function getRelativeLuminance(r: number, g: number, b: number): number {
  // Convert RGB to sRGB
  const rsRGB = r / 255
  const gsRGB = g / 255
  const bsRGB = b / 255

  // Apply gamma correction
  const rLinear = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4)
  const gLinear = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4)
  const bLinear = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4)

  // Calculate relative luminance using ITU-R BT.709 coefficients
  return 0.2126 * rLinear + 0.7152 * gLinear + 0.0722 * bLinear
}

/**
 * Extracts RGB values from various color formats
 * @param color Color string (hex, rgb, rgba, hsl, etc.) or computed style
 * @returns RGB values as [r, g, b] or null if parsing fails
 */
function parseColor(color: string): [number, number, number] | null {
  // Handle hex colors
  if (color.startsWith("#")) {
    const hex = color.slice(1)
    if (hex.length === 3) {
      const r = parseInt(hex[0] + hex[0], 16)
      const g = parseInt(hex[1] + hex[1], 16)
      const b = parseInt(hex[2] + hex[2], 16)
      return [r, g, b]
    } else if (hex.length === 6) {
      const r = parseInt(hex.slice(0, 2), 16)
      const g = parseInt(hex.slice(2, 4), 16)
      const b = parseInt(hex.slice(4, 6), 16)
      return [r, g, b]
    }
  }

  // Handle rgb() and rgba() colors
  const rgbMatch = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)/)
  if (rgbMatch) {
    return [parseInt(rgbMatch[1]), parseInt(rgbMatch[2]), parseInt(rgbMatch[3])]
  }

  // Handle named colors (basic set)
  const namedColors: Record<string, [number, number, number]> = {
    white: [255, 255, 255],
    black: [0, 0, 0],
    red: [255, 0, 0],
    green: [0, 128, 0],
    blue: [0, 0, 255],
    yellow: [255, 255, 0],
    cyan: [0, 255, 255],
    magenta: [255, 0, 255],
    gray: [128, 128, 128],
    grey: [128, 128, 128],
    transparent: [255, 255, 255] // Default to white for transparent
  }

  const normalizedColor = color.toLowerCase().trim()
  if (namedColors[normalizedColor]) {
    return namedColors[normalizedColor]
  }

  return null
}

/**
 * Gets the background color of an element by traversing up the DOM tree
 * @param element HTML element to analyze
 * @returns Background color string or 'white' as fallback
 */
function getElementBackgroundColor(element: HTMLElement): string {
  let currentElement: HTMLElement | null = element

  while (currentElement) {
    const computedStyle = window.getComputedStyle(currentElement)
    const backgroundColor = computedStyle.backgroundColor

    // Skip transparent backgrounds
    if (
      backgroundColor &&
      backgroundColor !== "transparent" &&
      backgroundColor !== "rgba(0, 0, 0, 0)"
    ) {
      return backgroundColor
    }

    currentElement = currentElement.parentElement
  }

  // Fallback to white if no background color is found
  return "white"
}

/**
 * Calculates the contrast ratio between two colors
 * @param luminance1 Relative luminance of first color
 * @param luminance2 Relative luminance of second color
 * @returns Contrast ratio (1-21)
 */
function getContrastRatio(luminance1: number, luminance2: number): number {
  const lighter = Math.max(luminance1, luminance2)
  const darker = Math.min(luminance1, luminance2)
  return (lighter + 0.05) / (darker + 0.05)
}

/**
 * Determines the appropriate text color (black or white) based on accessibility contrast ratios
 * @param element HTML element to analyze, or a color string
 * @returns CSS class name for text color ('text-black' or 'text-white')
 */
export function getAdaptativeColorClass(element: HTMLElement | string | null): string {
  let backgroundColor: string

  if (!element) {
    return "text-black" // Default fallback
  }

  // If element is a string, assume it's a color value
  if (typeof element === "string") {
    backgroundColor = element
  } else {
    backgroundColor = getElementBackgroundColor(element)
  }

  const rgbValues = parseColor(backgroundColor)
  if (!rgbValues) {
    return "text-black" // Fallback if color parsing fails
  }

  const [r, g, b] = rgbValues
  const backgroundLuminance = getRelativeLuminance(r, g, b)

  // Calculate luminance for black and white
  const blackLuminance = getRelativeLuminance(0, 0, 0) // Black: #000000
  const whiteLuminance = getRelativeLuminance(255, 255, 255) //

  // Calculate contrast ratios
  const blackContrast = getContrastRatio(backgroundLuminance, blackLuminance)
  const whiteContrast = getContrastRatio(backgroundLuminance, whiteLuminance)

  // Return the color with the better contrast ratio
  // WCAG AA requires a minimum contrast ratio of 4.5:1 for normal text
  return blackContrast >= whiteContrast ? "text-black" : "text-white"
}
