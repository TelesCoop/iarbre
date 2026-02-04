<script lang="ts" setup>
import { computed, watch, onMounted, onUnmounted, ref } from "vue"

type DrawerPosition = "left" | "right" | "top" | "bottom"

interface Props {
  visible: boolean
  position?: DrawerPosition
  customStyles?: {
    width?: string
    maxWidth?: string
    height?: string
    maxHeight?: string
  }
  headerTitle?: string
  modal?: boolean
  dismissable?: boolean
  dataCy?: string
}

interface Emits {
  (e: "update:visible", value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  position: "left",
  customStyles: () => ({}),
  headerTitle: "",
  modal: true,
  dismissable: true,
  dataCy: "app-drawer"
})

const emit = defineEmits<Emits>()
const drawerRef = ref<HTMLElement | null>(null)

const drawerVisible = computed({
  get: () => props.visible,
  set: (value: boolean) => emit("update:visible", value)
})

const close = () => {
  drawerVisible.value = false
}

const handleBackdropClick = () => {
  if (props.dismissable) {
    close()
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === "Escape" && props.dismissable) {
    close()
  }
}

const isHorizontal = computed(() => ["left", "right"].includes(props.position))

const drawerStyle = computed(() => {
  const defaultValue = isHorizontal.value
    ? { width: "90%", maxWidth: "25rem" }
    : { height: "auto", maxHeight: "90%" }

  return { ...defaultValue, ...props.customStyles }
})

const positionClasses = computed(() => {
  const base = "fixed z-[1000]"
  switch (props.position) {
    case "left":
      return `${base} top-0 left-0 h-full`
    case "right":
      return `${base} top-0 right-0 h-full`
    case "top":
      return `${base} top-0 left-0 w-full`
    case "bottom":
      return `${base} bottom-0 left-0 w-full`
    default:
      return base
  }
})

const slideTransform = computed(() => {
  switch (props.position) {
    case "left":
      return "translateX(-100%)"
    case "right":
      return "translateX(100%)"
    case "top":
      return "translateY(-100%)"
    case "bottom":
      return "translateY(100%)"
    default:
      return "translateX(-100%)"
  }
})

watch(
  () => props.visible,
  (newValue) => {
    if (newValue) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = ""
    }
  }
)

onMounted(() => {
  document.addEventListener("keydown", handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener("keydown", handleKeydown)
  document.body.style.overflow = ""
})
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer-fade">
      <div v-if="drawerVisible" class="drawer-backdrop" @click="handleBackdropClick" />
    </Transition>

    <Transition name="drawer-slide">
      <div
        v-if="drawerVisible"
        ref="drawerRef"
        :class="['app-drawer', positionClasses]"
        :style="drawerStyle"
        role="dialog"
        aria-modal="true"
        :data-cy="dataCy"
      >
        <div class="drawer-header">
          <slot name="header">
            <div v-if="$slots.icon || headerTitle" class="flex items-center gap-2">
              <slot name="icon" />
              <span v-if="headerTitle" class="font-semibold text-lg">{{ headerTitle }}</span>
            </div>
          </slot>
          <button
            type="button"
            class="drawer-close"
            aria-label="Fermer"
            data-cy="drawer-close"
            @click="close"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 14 14"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M1 1L13 13M1 13L13 1"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>

        <div class="drawer-content" data-cy="drawer-content">
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 999;
}

.app-drawer {
  background: white;
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.drawer-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.drawer-close:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}

.drawer-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem 1.25rem;
  overflow-y: auto;
  flex: 1;
}

.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.3s ease;
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: v-bind(slideTransform);
}
</style>
