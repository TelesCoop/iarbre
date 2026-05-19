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
        :data-cy="dataCy"
        :style="drawerStyle"
        aria-modal="true"
        role="dialog"
      >
        <div class="drawer-header">
          <slot name="header">
            <div v-if="$slots.icon || headerTitle" class="flex items-center gap-2">
              <slot name="icon" />
              <span v-if="headerTitle" class="font-semibold text-lg">{{ headerTitle }}</span>
            </div>
          </slot>
          <button
            aria-label="Fermer"
            class="drawer-close"
            data-cy="drawer-close"
            type="button"
            @click="close"
          >
            Fermer
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
@reference "@/styles/main.css";

.drawer-backdrop {
  @apply fixed inset-0 bg-black/40 z-[999];
}

.app-drawer {
  @apply flex flex-col overflow-hidden bg-white;
}

.drawer-header {
  @apply flex items-center justify-between shrink-0;
  @apply py-4 px-5;
  @apply border-b border-gray-200;
}

.drawer-close {
  @apply inline-flex items-center justify-center;
  @apply min-h-11 py-2 px-4;
  @apply bg-transparent border border-gray-200 rounded-lg;
  @apply text-sm font-medium font-sans text-gray-800;
  @apply cursor-pointer transition-all duration-200;
}

.drawer-close:hover {
  @apply bg-gray-100 border-gray-300;
}

.drawer-content {
  @apply flex flex-col flex-1 gap-4;
  @apply py-4 px-5;
  @apply overflow-y-auto;
}

.drawer-fade-enter-active,
.drawer-fade-leave-active {
  @apply transition-opacity duration-200;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  @apply opacity-0;
}

.drawer-slide-enter-active,
.drawer-slide-leave-active {
  @apply transition-transform duration-300;
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: v-bind(slideTransform);
}
</style>
