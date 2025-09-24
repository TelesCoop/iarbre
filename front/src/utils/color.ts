import { getContrast } from "polished"
import { getVulnerabilityColor } from "./vulnerability"

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

export function getPlantabilityTextColor(percentage: number | null): string {
  if (percentage === null || percentage === undefined) return "text-gray-300"
  if (percentage >= 80) return "text-scale-8"
  if (percentage >= 60) return "text-scale-6"
  if (percentage >= 40) return "text-scale-4"
  if (percentage >= 20) return "text-scale-2"
  return "text-scale-0"
}

export function getVulnerabilityTextColor(score: number | null): string {
  if (!score) return "text-gray-300"
  const colorCode = getVulnerabilityColor(score)
  const colorMap: Record<string, string> = {
    "#4474b5": "text-blue-600",
    "#75add1": "text-blue-400",
    "#aad9e9": "text-blue-200",
    "#5aaf7b": "text-green-600",
    "#9cbf4e": "text-green-500",
    "#d7e360": "text-green-300",
    "#fdae60": "text-orange-300",
    "#f56c43": "text-orange-500",
    "#d73026": "text-red-600",
    grey: "text-gray-500"
  }
  return colorMap[colorCode] || "text-gray-500"
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
