import { getContrast } from "polished"

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

export function getAdaptativeColorClass(
  element: HTMLElement | string | null,
  classPrefix: string = "text-"
): string {
  let backgroundColor: string

  const getCssClass = (color: string) => `${classPrefix}${color}`

  if (!element) {
    return getCssClass("black") // Default fallback
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
    return blackContrast >= whiteContrast ? getCssClass("black") : getCssClass("white")
  } catch (error) {
    // Fallback if color parsing fails
    return getCssClass("black") // Default fallback
  }
}
