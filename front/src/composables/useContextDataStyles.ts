import { computed } from "vue"

export const useContextDataStyles = () => {
  const CONTEXT_LIST_BASE_CLASSES = "space-y-3 pr-2"
  const SCROLLABLE_CLASSES =
    "max-h-44 xs:max-h-48 sm:max-h-52 md:max-h-56 lg:max-h-56 xl:max-h-100 overflow-y-auto"

  const getContextListClasses = (fullHeight = false, scrollable = false) => {
    if (!scrollable || fullHeight) {
      return CONTEXT_LIST_BASE_CLASSES
    }
    return `${SCROLLABLE_CLASSES} ${CONTEXT_LIST_BASE_CLASSES}`
  }

  const getContextListClassesComputed = (fullHeight: boolean, scrollable = false) => {
    return computed(() => getContextListClasses(fullHeight, scrollable))
  }

  return {
    CONTEXT_LIST_BASE_CLASSES,
    SCROLLABLE_CLASSES,
    getContextListClasses,
    getContextListClassesComputed
  }
}
