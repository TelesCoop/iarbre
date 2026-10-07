import { onClickOutside, useEventListener, type MaybeElementRef } from "@vueuse/core"

const DRAG_THRESHOLD_PX = 5

/**
 * Calls `handler` on a click outside `target`, except for the click a browser fires at the end
 * of a drag: panning the map is not a dismissal.
 */
export function useTapOutside(
  target: MaybeElementRef,
  handler: (event: PointerEvent) => void,
  options: { ignore?: MaybeElementRef[] } = {}
) {
  let pointerDownPosition: { x: number; y: number } | null = null

  useEventListener(
    window,
    "pointerdown",
    (event: PointerEvent) => {
      pointerDownPosition = { x: event.clientX, y: event.clientY }
    },
    { capture: true, passive: true }
  )

  onClickOutside(
    target,
    (event) => {
      const isDragEnd =
        pointerDownPosition !== null &&
        Math.hypot(event.clientX - pointerDownPosition.x, event.clientY - pointerDownPosition.y) >
          DRAG_THRESHOLD_PX
      if (!isDragEnd) handler(event)
    },
    options
  )
}
