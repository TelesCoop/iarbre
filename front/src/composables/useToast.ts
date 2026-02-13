import { ref, readonly } from "vue"

export type ToastSeverity = "success" | "info" | "warn" | "error"
export type ToastPosition = "top-left" | "top-right" | "bottom-left" | "bottom-right"

export interface ToastMessage {
  id: string
  severity: ToastSeverity
  summary: string
  detail?: string
  life?: number
  group?: string
}

interface ToastOptions {
  severity: ToastSeverity
  summary: string
  detail?: string
  life?: number
  group?: string
}

const toasts = ref<ToastMessage[]>([])

let toastIdCounter = 0

const generateId = (): string => {
  toastIdCounter++
  return `toast-${toastIdCounter}-${Date.now()}`
}

const add = (options: ToastOptions) => {
  const toast: ToastMessage = {
    id: generateId(),
    severity: options.severity,
    summary: options.summary,
    detail: options.detail,
    life: options.life ?? 3000,
    group: options.group
  }

  toasts.value.push(toast)

  if (toast.life && toast.life > 0) {
    setTimeout(() => {
      remove(toast.id)
    }, toast.life)
  }
}

const remove = (id: string) => {
  const index = toasts.value.findIndex((t) => t.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}

const removeAll = () => {
  toasts.value = []
}

export function useToast() {
  return {
    add,
    remove,
    removeAll,
    toasts: readonly(toasts)
  }
}

export { toasts }
