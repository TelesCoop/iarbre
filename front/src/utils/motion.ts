import { isPrintMode } from "@/utils/printMode"

export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") return false
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches
}

/**
 * Whether entrance animations should play: never for the PDF export (the page
 * is captured as soon as it is ready) nor for users who asked for less motion.
 */
export function shouldAnimate(): boolean {
  return !isPrintMode() && !prefersReducedMotion()
}

export function supportsIntersectionObserver(): boolean {
  return typeof window !== "undefined" && typeof IntersectionObserver !== "undefined"
}
