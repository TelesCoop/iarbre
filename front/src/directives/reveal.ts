import type { Directive } from "vue"
import { shouldAnimate, supportsIntersectionObserver } from "@/utils/motion"

/**
 * `v-reveal`: fades and slides the element in the first time it scrolls into
 * view. The optional value is a delay in milliseconds, used to stagger
 * siblings (`v-reveal="120"`). Styles live in main.css (`.reveal`).
 *
 * Does nothing in print mode or when the user prefers reduced motion: the
 * element is then displayed as is.
 */

const REVEAL_CLASS = "reveal"
const VISIBLE_CLASS = "reveal-visible"
const REVEAL_DURATION_MS = 600 // keep in sync with `.reveal` in main.css

let observer: IntersectionObserver | null = null
const delays = new WeakMap<Element, number>()

function getObserver(): IntersectionObserver {
  if (!observer) {
    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          const el = entry.target as HTMLElement
          const delay = delays.get(el) ?? 0
          el.style.transitionDelay = `${delay}ms`
          el.classList.add(VISIBLE_CLASS)
          observer?.unobserve(el)
          delays.delete(el)
          // The delay only concerns the entrance: drop it afterwards so that
          // other transitions on the element (hover shadows...) stay instant.
          setTimeout(() => {
            el.style.transitionDelay = ""
          }, delay + REVEAL_DURATION_MS)
        }
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.1 }
    )
  }
  return observer
}

export const vReveal: Directive<HTMLElement, number | undefined> = {
  beforeMount(el) {
    if (!shouldAnimate() || !supportsIntersectionObserver()) return
    el.classList.add(REVEAL_CLASS)
  },
  mounted(el, binding) {
    if (!el.classList.contains(REVEAL_CLASS)) return
    delays.set(el, binding.value ?? 0)
    getObserver().observe(el)
  },
  unmounted(el) {
    observer?.unobserve(el)
    delays.delete(el)
  }
}
