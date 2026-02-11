import type { Directive, DirectiveBinding } from "vue"

interface TooltipElement extends HTMLElement {
  _tooltip?: HTMLElement
  _tooltipText?: string
  _tooltipPosition?: string
  _showTooltip?: () => void
  _hideTooltip?: () => void
}

type TooltipPosition = "top" | "bottom" | "left" | "right"

const getPosition = (binding: DirectiveBinding): TooltipPosition => {
  if (binding.modifiers.top) return "top"
  if (binding.modifiers.bottom) return "bottom"
  if (binding.modifiers.left) return "left"
  if (binding.modifiers.right) return "right"
  return "top"
}

const createTooltip = (text: string, position: TooltipPosition): HTMLElement => {
  const tooltip = document.createElement("div")
  tooltip.className = `app-tooltip app-tooltip-${position}`
  tooltip.textContent = text
  tooltip.setAttribute("role", "tooltip")
  return tooltip
}

const positionTooltip = (tooltip: HTMLElement, target: HTMLElement, position: TooltipPosition) => {
  const rect = target.getBoundingClientRect()
  const tooltipRect = tooltip.getBoundingClientRect()
  const gap = 8

  let top = 0
  let left = 0

  switch (position) {
    case "top":
      top = rect.top - tooltipRect.height - gap
      left = rect.left + (rect.width - tooltipRect.width) / 2
      break
    case "bottom":
      top = rect.bottom + gap
      left = rect.left + (rect.width - tooltipRect.width) / 2
      break
    case "left":
      top = rect.top + (rect.height - tooltipRect.height) / 2
      left = rect.left - tooltipRect.width - gap
      break
    case "right":
      top = rect.top + (rect.height - tooltipRect.height) / 2
      left = rect.right + gap
      break
  }

  left = Math.max(8, Math.min(left, window.innerWidth - tooltipRect.width - 8))
  top = Math.max(8, Math.min(top, window.innerHeight - tooltipRect.height - 8))

  tooltip.style.top = `${top}px`
  tooltip.style.left = `${left}px`
}

export const vTooltip: Directive<TooltipElement> = {
  mounted(el, binding) {
    const text = binding.value
    if (!text) return

    const position = getPosition(binding)
    el._tooltipText = text
    el._tooltipPosition = position

    el._showTooltip = () => {
      if (!el._tooltipText) return

      // Remove existing tooltip first
      if (el._tooltip) {
        el._tooltip.remove()
        el._tooltip = undefined
      }

      const tooltip = createTooltip(el._tooltipText, position as TooltipPosition)
      document.body.appendChild(tooltip)
      el._tooltip = tooltip

      requestAnimationFrame(() => {
        if (el._tooltip === tooltip) {
          positionTooltip(tooltip, el, position as TooltipPosition)
          tooltip.classList.add("visible")
        }
      })
    }

    el._hideTooltip = () => {
      if (el._tooltip) {
        const tooltipToRemove = el._tooltip
        el._tooltip = undefined
        tooltipToRemove.remove()
      }
    }

    el.addEventListener("mouseenter", el._showTooltip)
    el.addEventListener("mouseleave", el._hideTooltip)
    el.addEventListener("focus", el._showTooltip)
    el.addEventListener("blur", el._hideTooltip)
  },

  updated(el, binding) {
    el._tooltipText = binding.value
    el._tooltipPosition = getPosition(binding)
  },

  unmounted(el) {
    if (el._showTooltip) {
      el.removeEventListener("mouseenter", el._showTooltip)
      el.removeEventListener("focus", el._showTooltip)
    }
    if (el._hideTooltip) {
      el.removeEventListener("mouseleave", el._hideTooltip)
      el.removeEventListener("blur", el._hideTooltip)
    }
    if (el._tooltip) {
      el._tooltip.remove()
      el._tooltip = undefined
    }
  }
}

export default vTooltip
