<script lang="ts" setup>
import { computed } from "vue"
import { toasts, useToast, type ToastPosition, type ToastSeverity } from "@/composables/useToast"

interface ToastProps {
  position?: ToastPosition
  group?: string
}

const props = withDefaults(defineProps<ToastProps>(), {
  position: "bottom-right",
  group: undefined
})

const { remove } = useToast()

const filteredToasts = computed(() => {
  if (props.group) {
    return toasts.value.filter((t) => t.group === props.group)
  }
  return toasts.value.filter((t) => !t.group)
})

const positionClasses = computed(() => {
  switch (props.position) {
    case "top-left":
      return "top-4 left-4"
    case "top-right":
      return "top-4 right-4"
    case "bottom-left":
      return "bottom-4 left-4"
    case "bottom-right":
    default:
      return "bottom-4 right-4"
  }
})

const severityStyles: Record<
  ToastSeverity,
  { bg: string; border: string; icon: string; iconColor: string }
> = {
  success: {
    bg: "bg-green-50",
    border: "border-green-200",
    icon: "M5 13l4 4L19 7",
    iconColor: "text-green-500"
  },
  info: {
    bg: "bg-blue-50",
    border: "border-blue-200",
    icon: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    iconColor: "text-blue-500"
  },
  warn: {
    bg: "bg-yellow-50",
    border: "border-yellow-200",
    icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
    iconColor: "text-yellow-500"
  },
  error: {
    bg: "bg-red-50",
    border: "border-red-200",
    icon: "M6 18L18 6M6 6l12 12",
    iconColor: "text-red-500"
  }
}
</script>

<template>
  <Teleport to="body">
    <div :class="['toast-container', positionClasses]">
      <TransitionGroup name="toast">
        <div
          v-for="toast in filteredToasts"
          :key="toast.id"
          :class="[
            'toast-item',
            severityStyles[toast.severity].bg,
            severityStyles[toast.severity].border
          ]"
          role="alert"
        >
          <div class="toast-icon" :class="severityStyles[toast.severity].iconColor">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                :d="severityStyles[toast.severity].icon"
              />
            </svg>
          </div>
          <div class="toast-content">
            <div class="toast-summary">{{ toast.summary }}</div>
            <div v-if="toast.detail" class="toast-detail">{{ toast.detail }}</div>
          </div>
          <button type="button" class="toast-close" aria-label="Fermer" @click="remove(toast.id)">
            <svg
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" d="M1 1L13 13M1 13L13 1" />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 24rem;
  pointer-events: none;
}

.toast-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border: 1px solid;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  pointer-events: auto;
}

.toast-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-summary {
  font-weight: 600;
  font-size: 0.875rem;
  color: #1f2937;
}

.toast-detail {
  font-size: 0.813rem;
  color: #4b5563;
  margin-top: 0.25rem;
}

.toast-close {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 0.25rem;
  transition: all 0.15s;
}

.toast-close:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #4b5563;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
