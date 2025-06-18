import { getContrast } from "polished"

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

  try {
    // Use polished to calculate contrast ratios with black and white
    const blackContrast = getContrast(backgroundColor, "#000000")
    const whiteContrast = getContrast(backgroundColor, "#ffffff")

    // Return the color with the better contrast ratio
    // WCAG AA requires a minimum contrast ratio of 4.5:1 for normal text
    return blackContrast >= whiteContrast ? "text-black" : "text-white"
  } catch (error) {
    // Fallback if color parsing fails
    return "text-black"
  }
}
